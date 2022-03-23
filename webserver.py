from flask import Flask, request
from itsdangerous import json
from werkzeug import Response
import requests

app = Flask(__name__)

@app.route("/")
def main():
  return Response("Success")

@app.route("/github",methods=["GET", "POST"])
def github():
    print(request.headers)
    if request.headers.get("X-Github-Event") == "push":
      print(len(request.json['commits']))
      requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':"🔔 New Commit!",
                    'url':request.json.get('commits_url'),
                    'color':0x6D00FF,
                    'description':f'**{len(request.json["commits"])}** Commits on {request.json.get("repository")["full_name"]}\n\n**Commit by** {request.json.get("commits")[0]["author"]["username"]}\n\n**Message** {request.json.get("commits")[0]["message"]}\n\n**Commit URL**: {request.json.get("commits_url")}'
                    
                }
            ]
        })
    elif request.headers.get("X-Github-Event") == "pull_request":
      requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':"📈 Pull Request!",
                    'color':0x6D00FF,
                    'description':f'Pull Request {request.json.get("action")} on {request.json.get("base")["repo"]["full_name"]}\n\n**User** {request.json.get("pull_request")["base"]["user"]["login"]}\n\n**Message** {request.json.get("pull_request")["title"]}'
                }
            ]
        })
    elif request.headers.get("X-Github-Event") == "issues":
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':"‼ New Issue!",
                    'color':0x6D00FF,
                    'description':f'Issue {request.json.get("action")} on {request.json["repo"]["full_name"]}\n\n**User** {request.json.get["sender"]["login"]}\n\n**URL** {request.json.get("issue")["html_url"]}'
                }
            ]
        })
        
    elif request.headers.get("X-Github-Event") == "issue_comment":
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':"⁉ Issue Commented",
                    'color':0x6D00FF,
                    'description':f'Issue {request.json.get("action")} on {request.json["repo"]["full_name"]}\n\n**User** {request.json.get["sender"]["login"]}\n\n**URL** {request.json.get("issue")["html_url"]}'
                }
            ]
        })
        
    elif request.headers.get("X-Github-Event") == "create":
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':f"➕ Created!",
                    'color':0x6D00FF,
                    'description':f'A {request.json.get("ref_type")}: {request.json.get("issue")} was created on {request.json["repository"]["full_name"]}\n\n**User** {request.json.get["sender"]["login"]}\n\n__**Repo**__: {request.json["repository"]["full_name"]}\n\n__**User**__: {request.json["sender"]["login"]}'
                }
            ]
        })
        
    elif request.headers.get("X-Github-Event") == "member":
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':f"👥 Collabs updated",
                    'color':0x6D00FF,
                    'description':f'Collaborator: {request.json.get("member")["login"]} {request.json.get("member")["login"]} on {request.json["repository"]["full_name"]}'
                }
            ]
        })

    elif request.headers.get("X-Github-Event") == "gollum":
        acts = ""
        for i in request.json.get("pages"):
            acts += "\n"+i["title"]+"\n"+i["action"]
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':f"📜 Wiki updated",
                    'color':0x6D00FF,
                    'description':f'User: {request.json.get("sender")["login"]} on {request.json["repository"]["full_name"]}\n\n{acts}\n\n__**Repo**__: {request.json["repository"]["full_name"]}\n\n__**User**__: {request.json["sender"]["login"]}'
                }
            ]
        })
        
    elif request.headers.get("X-Github-Event") == "watch":
        requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':f"🌟 Stars updated!",
                    'color':0x6D00FF,
                    'description':f'Woah, {request.json["sender"]["login"]} starred the Repo!\n\n__**Repo**__: {request.json["repository"]["full_name"]}\n\n__**User**__: {request.json["sender"]["login"]}'
                }
            ]
        })


    return Response("success")

app.run("0.0.0.0",80)
