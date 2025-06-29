#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单Elasticsearch模拟服务器
用于演示分布式存储功能
"""

from flask import Flask, jsonify, request
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)

# 模拟集群数据
cluster_data = {
    "cluster_name": "house-data-cluster",
    "status": "green",
    "timed_out": False,
    "number_of_nodes": 3,
    "number_of_data_nodes": 3,
    "active_primary_shards": 3,
    "active_shards": 6,
    "relocating_shards": 0,
    "initializing_shards": 0,
    "unassigned_shards": 0,
    "delayed_unassigned_shards": 0,
    "number_of_pending_tasks": 0,
    "number_of_in_flight_fetch": 0,
    "task_max_waiting_in_queue_millis": 0,
    "active_shards_percent_as_number": 100.0
}

nodes_data = {
    "cluster_name": "house-data-cluster",
    "nodes": {
        "node1": {
            "name": "node-1",
            "transport_address": "127.0.0.1:9300",
            "host": "127.0.0.1",
            "ip": "127.0.0.1",
            "version": "7.17.0",
            "roles": ["master", "data", "ingest"]
        },
        "node2": {
            "name": "node-2", 
            "transport_address": "127.0.0.1:9301",
            "host": "127.0.0.1",
            "ip": "127.0.0.1",
            "version": "7.17.0",
            "roles": ["data", "ingest"]
        },
        "node3": {
            "name": "node-3",
            "transport_address": "127.0.0.1:9302", 
            "host": "127.0.0.1",
            "ip": "127.0.0.1",
            "version": "7.17.0",
            "roles": ["data", "ingest"]
        }
    }
}

indices_data = [
    {
        "health": "green",
        "status": "open", 
        "index": "house_data",
        "uuid": "abc123",
        "pri": "3",
        "rep": "1", 
        "docs.count": "1000",
        "docs.deleted": "0",
        "store.size": "2.1mb",
        "pri.store.size": "1.1mb"
    }
]

@app.route('/')
def root():
    return jsonify({
        "name": "node-1",
        "cluster_name": "house-data-cluster",
        "cluster_uuid": "abc123def456",
        "version": {
            "number": "7.17.0",
            "build_flavor": "default",
            "build_type": "zip",
            "build_hash": "bee86328705acaa9a6daede7140defd4d9ec56bd",
            "build_date": "2022-01-28T08:36:04.875279988Z",
            "build_snapshot": False,
            "lucene_version": "8.11.1",
            "minimum_wire_compatibility_version": "6.8.0",
            "minimum_index_compatibility_version": "6.0.0-beta1"
        },
        "tagline": "You Know, for Search"
    })

@app.route('/_cluster/health')
def cluster_health():
    return jsonify(cluster_data)

@app.route('/_nodes')
def nodes_info():
    return jsonify(nodes_data)

@app.route('/_cat/indices')
def cat_indices():
    if request.args.get('format') == 'json':
        return jsonify(indices_data)
    else:
        # 返回表格格式
        result = "health status index     uuid   pri rep docs.count docs.deleted store.size pri.store.size\n"
        for idx in indices_data:
            result += f"{idx['health']} {idx['status']} {idx['index']} {idx['uuid']} {idx['pri']} {idx['rep']} {idx['docs.count']} {idx['docs.deleted']} {idx['store.size']} {idx['pri.store.size']}\n"
        return result, 200, {'Content-Type': 'text/plain'}

@app.route('/_cat/shards')
def cat_shards():
    shards_data = [
        "house_data 0 p STARTED 334 1.1mb 127.0.0.1 node-1",
        "house_data 0 r STARTED 334 1.1mb 127.0.0.1 node-2", 
        "house_data 1 p STARTED 333 1.0mb 127.0.0.1 node-2",
        "house_data 1 r STARTED 333 1.0mb 127.0.0.1 node-3",
        "house_data 2 p STARTED 333 1.0mb 127.0.0.1 node-3",
        "house_data 2 r STARTED 333 1.0mb 127.0.0.1 node-1"
    ]
    
    if request.args.get('format') == 'json':
        return jsonify([{
            "index": "house_data",
            "shard": i % 3,
            "prirep": "p" if i < 3 else "r", 
            "state": "STARTED",
            "docs": 333 + (1 if i == 0 else 0),
            "store": "1.1mb" if i == 0 else "1.0mb",
            "ip": "127.0.0.1",
            "node": f"node-{(i % 3) + 1}"
        } for i in range(6)])
    else:
        result = "index    shard prirep state   docs store ip        node\n"
        result += "\n".join(shards_data)
        return result, 200, {'Content-Type': 'text/plain'}

@app.route('/house_data/_search', methods=['GET', 'POST'])
def search_houses():
    # 模拟搜索结果
    search_result = {
        "took": 2,
        "timed_out": False,
        "_shards": {
            "total": 3,
            "successful": 3,
            "skipped": 0,
            "failed": 0
        },
        "hits": {
            "total": {
                "value": 1000,
                "relation": "eq"
            },
            "max_score": 1.0,
            "hits": [
                {
                    "_index": "house_data",
                    "_type": "_doc", 
                    "_id": "1",
                    "_score": 1.0,
                    "_source": {
                        "title": "精装修整租房源",
                        "city": "广州",
                        "district": "天河区",
                        "price": 4500,
                        "area": 80
                    }
                }
            ]
        }
    }
    return jsonify(search_result)

@app.route('/test_index', methods=['PUT'])
def create_test_index():
    return jsonify({"acknowledged": True, "shards_acknowledged": True, "index": "test_index"})

@app.route('/test_index', methods=['DELETE'])
def delete_test_index():
    return jsonify({"acknowledged": True})

def run_server():
    """在后台运行服务器"""
    app.run(host='127.0.0.1', port=9200, debug=False, use_reloader=False)

def start_elasticsearch_mock():
    """启动Elasticsearch模拟服务"""
    print("🚀 启动Elasticsearch模拟服务...")
    print("📍 地址: http://127.0.0.1:9200")
    print("🔍 集群健康: http://127.0.0.1:9200/_cluster/health")
    print("📊 节点信息: http://127.0.0.1:9200/_nodes")
    
    # 在后台线程中运行
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    print("✅ Elasticsearch模拟服务已启动")
    
    return server_thread

if __name__ == '__main__':
    start_elasticsearch_mock()
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止Elasticsearch模拟服务")
