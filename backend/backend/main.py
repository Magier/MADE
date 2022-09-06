import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/data")
async def data():
    nodes = [
        {"name": "frontend-1", "kind": "pod", "namespace": "dmz", "part_of": "frontend"},
        {"name": "frontend-2", "kind": "pod", "namespace": "dmz", "part_of": "frontend"},
        {"name": "frontend", "kind": "service", "namespace": "dmz", "part_of": "frontend"},
        {"name": "frontend", "kind": "deployment", "namespace": "dmz", "part_of": "frontend"},
        {"name": "frontend", "namespace": "dmz" },
        # proxy service
        {"name": "proxy-service", "namespace": "dmz"},
        {"name": "proxy-service", "kind": "deployment", "namespace": "dmz", "part_of": "proxy-service"},
        {"name": "proxy-service", "kind": "pod", "namespace": "dmz", "part_of": "proxy-service"},
        {"name": "proxy-service", "kind": "service", "namespace": "dmz", "part_of": "proxy-service"},
        {"name": "proxy", "kind": "serviceaccount", "namespace": "dmz", "part_of": "proxy-service"},
        {"name": "proxy-role", "kind": "role", "namespace": "dmz", "part_of": "proxy-service"},
        {"name": "proxy-rolebinding", "kind": "rolebinding", "namespace": "dmz", "part_of": "proxy-service"},
        # ad service
        {"name": "ad-service", "namespace": "dmz"},
        {"name": "ad-service", "kind": "deployment", "namespace": "dmz", "part_of": "ad-service"},
        {"name": "ad-service", "kind": "pod", "namespace": "dmz", "part_of": "ad-service"},
        {"name": "ad-service", "kind": "service", "namespace": "dmz", "part_of": "ad-service"},
        # user-auth service
        {"name": "user-auth-service", "namespace": "dmz"},
        {"name": "user-auth-service", "kind": "deployment", "namespace": "dmz", "part_of": "user-auth-service"},
        {"name": "user-auth-service", "kind": "pod", "namespace": "dmz", "part_of": "user-auth-service"},
        {"name": "user-auth-service", "kind": "service", "namespace": "dmz", "part_of": "user-auth-service"},
        # redis
        {"name": "redis", "namespace": "dmz"},
        {"name": "redis", "kind": "deployment", "namespace": "dmz", "part_of": "redis"},
        {"name": "redis", "kind": "pod", "namespace": "dmz", "part_of": "redis"},
        {"name": "redis", "kind": "service", "namespace": "dmz", "part_of": "redis"},
        # DB
        {"name": "db", "namespace": "dmz", "node": "worker"},
        {"name": "db", "kind": "pod", "namespace": "dmz", "part_of": "db"},
        {"name": "db", "kind": "configmap", "namespace": "dmz", "part_of": "db"},
        {"name": "db", "kind": "statefulset", "namespace": "dmz", "part_of": "db"},
        {"name": "db", "kind": "service", "namespace": "dmz", "part_of": "db"},
        {"name": "db", "kind": "secret", "namespace": "dmz", "part_of": "db"},
        {"name": "db", "kind": "serviceaccount", "namespace": "dmz", "part_of": "db"},

        # attacker pod
        {"name": "attacker-c2", "namespace": "attacker-den"},
        {"name": "attacker-c2", "kind": "pod", "namespace": "attacker-den", "part_of": "attacker-c2"},


        # other
        {"name": "Internet"},
        {"name": "worker", "kind": "node", "part-of": "kind-cluster"},
        {"name": "control-plane", "kind": "node", "part-of": "kind-cluster"},
        {"name": "control-plane", "kind": "control-plane", "node": "control-plane"},
        
        {"name": "kind-cluster", "kind": "cluster"},
        {"name": "app", "kind": "ingress", "namespace": "dmz"},
        {"name": "cluster-admin", "kind": "clusterrole", "part_of": "kind-cluster"},

        {"name": "default", "kind": "namespace", "part_of": "kind-cluster"},
        {"name": "dmz", "kind": "namespace", "part_of": "kind-cluster"},
        {"name": "attacker-den", "kind": "namespace", "part_of": "kind-cluster"},
        {"name": "kube-system", "kind": "namespace", "part_of": "control-plane/control-plane"},
    ]
    edges = [
        # frontend
        {"from": "deployment/frontend", "to": "pod/frontend-1", "relation": "manages"},
        {"from": "deployment/frontend", "to": "pod/frontend-2", "relation": "manages"},
        {"from": "service/frontend", "to": "pod/frontend-1", "relation": "targets"},
        {"from": "service/frontend", "to": "pod/frontend-2", "relation": "targets"},
        {"from": "ingress/app", "to": "service/frontend", "relation": "routes", "port": 80, "path": "/ui"},

        # proxy service
        {"from": "service/proxy-service", "to": "pod/proxy-service", "relation": "targets"},
        {"from": "deployment/proxy-service", "to": "pod/proxy-service", "relation": "manages"},
        {"from": "rolebinding/proxy-rolebinding", "to": "serviceaccount/proxy", "relation": "subject"},
        {"from": "rolebinding/proxy-rolebinding", "to": "role/proxy-role", "relation": "binds"},
        {"from": "pod/proxy-service", "to": "serviceaccount/proxy", "relation": "uses"},

        # ad service
        {"from": "deployment/ad-service", "to": "pod/ad-service", "relation": "manages"},
        {"from": "service/ad-service", "to": "pod/ad-service", "relation": "targets"},
        {"from": "ingress/app", "to": "service/ad-service", "relation": "routes", "port": 80, "path": "/ad-service"},

        # user-auth service
        {"from": "service/user-auth-service", "to": "pod/user-auth-service", "relation": "targets"},
        {"from": "deployment/user-auth-service", "to": "pod/user-auth-service", "relation": "manages"},
        {"from": "pod/user-auth-service", "to": "secret/db", "relation": "uses"},

        # redis
        {"from": "service/redis", "to": "pod/redis", "relation": "targets"},
        {"from": "deployment/redis", "to": "pod/redis", "relation": "manages"},

        # db
        {"from": "service/db", "to": "pod/db", "relation": "targets"},
        {"from": "statefulset/db", "to": "pod/db", "relation": "manages"},
        {"from": "pod/db", "to": "secret/db", "relation": "uses"},
        {"from": "pod/db", "to": "serviceaccount/db", "relation": "uses"},
        {"from": "pod/db", "to": "configmap/db", "relation": "uses"},

        # misc relations
        {"from": "Internet", "to": "ingress/app"},
        {"from": "proxy-service", "to": "Internet"},
        {"from": "frontend", "to": "user-auth-service", "relation": "communicates-with"},
        {"from": "frontend", "to": "ad-service", "relation": "communicates-with"},
        {"from": "frontend", "to": "proxy-service", "relation": "communicates-with"},
        {"from": "user-auth-service", "to": "db", "relation": "communicates-with"},

        {"from": "pod/attacker-c2", "to": "pod/frontend-1", "relation": "attacks"}
    ]

    return {"nodes": nodes, "edges": edges}


@app.get("/oas_data")
async def oas_data():
    print(os.getcwd())
    with open("data/refs_cyjs.json", "r") as f:
        data = json.load(f)
        return data["elements"]


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
