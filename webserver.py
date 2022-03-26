from flask import Flask, redirect, render_template, request, url_for
from werkzeug import Response
import requests
from flask_dance.contrib.github import make_github_blueprint,github 

app = Flask(__name__)
app.config["SECRET_KEY"] = "636c626fbb87e4b10d7b"
gh_blueprint = make_github_blueprint(
    client_id="636c626fbb87e4b10d7b",
    client_secret="91a813e210f2eadbcf3ab19839f3a387ee54454b",
)
app.register_blueprint(gh_blueprint,url_prefix="/oauth")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/source")
def src():
    return redirect("https://github.com/HdlJohanna/GitHubBot")

@app.route("/discord")
def dc():
    return redirect("https://discord.gg/RVppWSxK3P")

@app.route("/invite")
def invite():
    return redirect("Linhttps://discord.com/oauth2/authorize?client_id=899236006769860658&scope=bot&permissions=536963313")


@app.route("/oauth/github/authorized")
def authed():
    code = request.args.get("code")
    resp = requests.post("https://github.com/login/oauth/access_token",data={
        "state":"oauthme",
        "client_id":"636c626fbb87e4b10d7b",
        "client_secret":"91a813e210f2eadbcf3ab19839f3a387ee54454b",
        "redirect_uri":"https://github.zerotwo36.repl.co/oauth/github/authorized",
        "code":code
    })
    return resp.json()

@app.route("/github",methods=["GET", "POST"])
def github_():
    print(request.headers)
    if request.headers.get("X-Github-Event") == "push":
      print(len(request.json['commits']))
      url = f'https://github.com/{request.json.get("repository")["full_name"]}/commits/{request.json["commits"][-1]["id"]}'
      requests.post(request.args.get("payload"), json={
            'embeds':[
                {
                    'title':"🔔 New Commit!",
                    'color':0x6D00FF,
                    'description':f'**{len(request.json["commits"])}** Commits on {request.json.get("repository")["full_name"]}\n\n**Commit by** {request.json.get("commits")[0]["author"]["username"]}\n\n**Message** {request.json.get("commits")[-1]["message"]}\n\n**Commit URL**: {url}'
                    
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
                    'description':f'Collaborator: {request.json.get("member")["login"]} on {request.json["repository"]["full_name"]}'
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
