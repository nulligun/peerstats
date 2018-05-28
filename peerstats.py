from flask import Flask, jsonify, request, make_response, redirect, url_for, send_from_directory
from flask_restful import Resource, Api
from models import *
from configobj import ConfigObj
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
import json
import re

app = Flask(__name__)
CORS(app)
config = ConfigObj(".env")
engine = create_engine("mysql+mysqldb://%(database_user)s:%(database_password)s@%(database_host)s/%(database_name)s" % config, isolation_level="READ UNCOMMITTED", pool_recycle=4)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


app.config['UPLOAD_FOLDER'] = config['upload_folder']


@app.route('/json', methods=['GET'])
def json():
    peers = session.query(Peer).all()
    results = []
    for p in peers:
        results.append({'address': p.address, 'name': p.name, 'id': p.enode, 'ready': is_node_ready(p)})

    return jsonify(results)

def is_parity_node(node):
    p = re.match('^Parity\/', node.name)
    if p:
        return True

def is_node_ready(node):
    p = re.match('^Parity\/v1\.(\d+.\d+)\-', node.name)
    if p:
        version = float(p[1])
        if version < 10.3:
            return False
        else:
            return True

    return False


@app.route('/html', methods=['GET'])
def html():
    peers = session.query(Peer).all()
    nodes_table = []
    results = []
    nodes_table.append('<div><table width="100%"><tr><th align="left">Name</th><th align="left">Address</th><th>Ready</th><th align="right">Last Update</th>')
    total_nodes = 0
    nodes_ready = 0
    parity_upgrade_needed = 0
    geth_or_other = 0
    newlist = sorted(peers, key=lambda k: ('z' if is_node_ready(k) else 'y') + k.name)
    for p in newlist:
        node_ready = is_node_ready(p)
        total_nodes = total_nodes + 1
        if node_ready:
            nodes_ready = nodes_ready + 1
        else:
            if is_parity_node(p):
                parity_upgrade_needed = parity_upgrade_needed + 1
            else:
                geth_or_other = geth_or_other + 1

        nodes_table.append('<tr><td align="left">' + p.name + '</td><td align="left">' + p.address + '</td><td align="center">' + str(node_ready) + '</td><td align="right">' + str(p.date_updated) + '</td></tr>')

    nodes_table.append('</table>')

    percent = int((nodes_ready / total_nodes) * 100)
    results.append('<table>')
    results.append('<tr><th>Percent Ready</th><td>' + str(percent) + '</td></tr>')
    results.append('<tr><th>Total Nodes</th><td>' + str(total_nodes) + '</td></tr>')
    results.append('<tr><th>Nodes Ready</th><td>' + str(nodes_ready) + '</td></tr>')
    results.append('<tr><th>Parity Nodes Needing Upgrade</th><td>' + str(parity_upgrade_needed) + '</td></tr>')
    results.append('<tr><th>Geth Nodes Needing Upgrade</th><td>' + str(geth_or_other) + '</td></tr>')
    results.append('</table>')

    results.extend(nodes_table)

    results.append('</div>')

    return ''.join(results)


@app.route('/', methods=['GET', 'POST'])
def peerstats():
    if request.method == 'POST':
        file = request.files['file']
        added = 0
        updated = 0
        if file:
            data = json.loads(file.read())
            peers = data['result']['peers']
            for p in peers:
                if p['id'] is None:
                    continue
                if p['network']['remoteAddress'] == 'Handshake':
                    continue

                peer = session.query(Peer).filter_by(enode=p['id']).one_or_none()
                if not peer:
                    peer = Peer()
                    peer.name = p['name']
                    peer.enode = p['id']
                    peer.address = p['network']['remoteAddress']
                    peer.peer_data = json.dumps(p)
                    session.add(peer)
                    added = added + 1
                else:
                    peer.name = p['name']
                    peer.enode = p['id']
                    peer.address = p['network']['remoteAddress']
                    peer.peer_data = json.dumps(p)
                    updated = updated + 1

                session.commit()

            return redirect(url_for('peerstats', added=added, updated=updated))

    return '''
    <!doctype html>
    <head>
    <title>Peer Stats</title>
    </head>
    <body>
    <p>Run the following command on your node to create a peers.json file.  Upload that file on this form to add your list of peers to help make the fork transition easier.</p>
    <blockquote>
    curl --data '{"method":"parity_netPeers","params":[],"id":1,"jsonrpc":"2.0"}' -H "Content-Type: application/json" -X POST localhost:8545 > peers.json
    </blockquote>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <div id="all-peers"></div>
    <script src="/js/peerstats.js" type="application/javascript"></script>
    </body>
    </html>
    '''


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path, mimetype='application/javascript')


app.run(debug=True)
