from datetime import datetime
import contextlib
import io
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.request import Request
from github import Github
from pyramid.threadlocal import get_current_request
from nextcord.ext import commands
import json
from threading import Thread
import nextcord
import github
import requests
from cryptography.fernet import Fernet

import os
class Logger:
    @staticmethod
    def log(logfile:os.PathLike,*,text:str):
        with open(logfile,"r") as f:
            _log = f.read()
            _log += "\n"+text
        with open(logfile,"w+") as f:
            f.write(_log)

        return 0

    @staticmethod
    def getlog(logfile:os.PathLike):
        return open(logfile,"r").read()



class SysLog:
    def __init__(self):
        self.logger = Logger

    def info(self,*args):
        self.logger.log("logfile.log",text=f"{datetime.now()} INFO "+" ".join(args))        
    def warn(self,*args):
        self.logger.log("logfile.log",text=f"{datetime.now()} WARN "+" ".join(args))            
    def error(self,*args):
        self.logger.log("logfile.log",text=f"{datetime.now()} ERROR "+" ".join(args))        
    


client = commands.Bot(command_prefix='gh ')
logger = SysLog()


@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    await client.change_presence(activity=nextcord.Game(name="People type `gh help`"))

@client.group(name="org")
async def _org(ctx):
    pass

@_org.command()
async def hook_create(ctx,org,url="https://webhook.site"):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    orga = git.get_organization(org)    
    EVENTS = ["push", "pull_request","issues","issue_comment","create","member","gollum","watch","release","delete","fork","pull_request_review_comment"]
    logger.info(f'Webhook ORG {org} create')
    orga.create_hook("web",{        
        "url": url,
        "content_type": "json"},EVENTS, active=True)

@_org.command()
async def repo(ctx,org,repo_name):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    orga = git.get_organization(org)
    
    r = orga.get_repo(repo_name)
    embed = nextcord.Embed(title=f"{r.name}",description=r.description,color=nextcord.Color.dark_magenta(),url=r.clone_url)
    
    embed.add_field(name="Stars",value=r.stargazers_count)
    embed.add_field(name="Forks",value=r.forks_count)
    embed.add_field(name="Active?",value=not r.archived)
    embed.add_field(name="Created",value=r.created_at)
    embed.add_field(name="Watchers",value=r.watchers_count)
    embed.add_field(name="Subscriptions",value=r.subscribers_count)
    embed.add_field(name="Last Update",value=r.updated_at)
    await ctx.send(embed=embed)

@client.group()
async def repo(ctx):
    ...

@client.group()
async def issue(ctx):...

@issue.command()
async def create(ctx,name,title:str,*,body:str):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    logger.info(f'Issue {name} created')
    repo = git.get_repo(name)
    repo.create_issue(title,body)
    await ctx.send(":ok_hand: Issue created successfully!")
    
@issue.command()
async def find(ctx,name,idx):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    repo = git.get_repo(name)
    issue = repo.get_issue(idx)
    embed = nextcord.Embed(title=issue.title,description=issue.body)
    embed.set_author(name=issue.assignee.name,icon_url=issue.assignee.avatar_url)
    await ctx.send(embed=embed)

@repo.command()
async def info(ctx,repo_name):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    
    r = git.get_repo(repo_name)
    embed = nextcord.Embed(title=f"{r.name}",description=r.description,color=nextcord.Color.dark_magenta(),url=r.clone_url)
    embed.add_field(name="Stars",value=r.stargazers_count)
    embed.add_field(name="Forks",value=r.forks_count)
    embed.add_field(name="Active?",value=not r.archived)
    embed.add_field(name="Created",value=r.created_at)
    embed.add_field(name="Watchers",value=r.watchers_count)
    embed.add_field(name="Subscriptions",value=r.subscribers_count)
    embed.add_field(name="Last Update",value=r.updated_at)
    await ctx.send(embed=embed)


@repo.command()
async def collab(ctx,action,repo_name,*users):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    logger.info(f'Collab {action} on {repo_name} (Users: {users})')
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    
    r = git.get_repo(repo_name)
    
    for user in users:
      if action.lower() == "add":
        r.add_to_collaborators(user,"admin")
      elif action.lower() == "remove":
        r.remove_from_collaborators(user)
    await ctx.send(f'Collabs Updated!')

@repo.error
async def on_error(ctx,ex):
    logger.error(f'{ex}')
    await ctx.send(f':x: Error: %s' % ex)

@issue.error
async def on_error(ctx,ex):
    logger.error(f'{ex}')
    await ctx.send(f':x: Error: %s' % ex)

@repo.command()
async def pull(ctx,reponame,title,base,head,*,body):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You haven't synced your Profile to a GitHub account yet: `gh init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    
    repo = git.get_repo(reponame)
    pull = repo.create_pull(title,body,base,head)
    logger.info(f"PULLED {ctx.author.name}")
    embed = nextcord.Embed(title="Pull done!",description=f"You pulled into {pull.title}. Now we wait...",color=nextcord.Color.dark_magenta())
    await ctx.send(embed=embed)

@repo.command(aliases=["deletefile","dfile"])
async def df(ctx,reponame,path,*,message):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You haven't synced your Profile to a GitHub account yet: `gh init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    
    repo = git.get_repo(reponame)
    repo.delete_file(path,message)
    logger.info(f"DELETE {path} ({message})")
    embed = nextcord.Embed(title=f"File Deleted!",description=f"{path} has been deleted successfully",color=nextcord.Color.dark_magenta())
    await ctx.send(embed=embed)


@client.group()
async def init(ctx):
    ...

@init.command()
async def keyremove(ctx):
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You haven't synced your Profile to a GitHub account yet: `gh init key`")
    config.pop(str(ctx.author.id))
    with open("config.json","w") as f:
        json.dump(config,f)
    logger.info(f"Data removed for user {ctx.author.name}")
    await ctx.send(":ok_hand: All your Data was removed!")

@init.command()
async def logs(ctx,repository,channel:nextcord.TextChannel,events=""):
    
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    webhooks = await channel.webhooks()
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    githook = nextcord.utils.get(webhooks,name="GitHub")
    if not githook:
        githook = await channel.create_webhook(name="GitHub",avatar=await client.user.avatar.read())
    EVENTS = ["push", "pull_request","issues","issue_comment","create","member","gollum","watch","release","delete","fork","pull_request_review_comment"]
    repo = git.get_repo(repository)
    await ctx.send(":information_source: Creating Webhook for Repository "+repo.name)
    create_webhook(githook.url,*repository.split("/"),ctx.author.id)
    embed = nextcord.Embed(title='Webhook created!',color=nextcord.Color.dark_magenta(),description=f'A Webhook was created for {repository} by [{git.get_user().name}]({git.get_user().url})')
    await githook.send(embed=embed)


ENDPOINT = "github"

def create_webhook(payload_url,owner,repo_name, user_id):
    """ Creates a webhook for the specified repository.

    This is a programmatic approach to creating webhooks with PyGithub's API. If you wish, this can be done
    manually at your repository's page on Github in the "Settings" section. There is a option there to work with
    and configure Webhooks.
    """
    
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        configjson = json.load(f)
    EVENTS = ["push", "pull_request","issues","issue_comment","create","member","gollum","watch","release","delete","fork","pull_request_review_comment"]

    HOST = "github.zerotwo36.repl.co"

    config = {
        "url": "https://{host}/{endpoint}?payload={guild_id}".format(host=HOST, endpoint=ENDPOINT,guild_id=payload_url),
        "content_type": "json"
    }
    
    g = Github(fernet.decrypt(configjson[str(user_id)].encode()).decode('utf-8'))
    repo = g.get_repo(f"{owner}/{repo_name}")
    repo.create_hook("web", config, EVENTS, active=True)


def serve_hooks():
    config = Configurator()


    config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
    config.scan()

    app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 80, app)
    server.serve_forever()


@logs.error
async def event_log_error(ctx,error):
    await ctx.send(f':x: %s' % error)

@client.command()
async def privacy(ctx):
    await ctx.send(file=nextcord.File("privacy.txt"))

@client.command()
async def me(ctx):
    
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    
    embed = nextcord.Embed(title='Your Information',description=f'Change it using `gh init key`')
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    user = git.get_user()
    embed.add_field(name="Personal Access Token",value=config[str(ctx.author.id)])
    embed.add_field(name="Username",value=user.login)
    embed.add_field(name="Email",value=user.email)
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.author.send(embed=embed)

@init.command()
async def key(ctx):
    await ctx.author.send("Please enter your GitHub Auth Key or type `auth cancel` to cancel.\n\n")
    await ctx.author.send("Please also consider Reading `gh privacy` and reassure yourself that we're using the right things `gh me`")
    await ctx.author.send("Also know that you can always delete this key using `gh init keyremove`. All of your Data will be eradicated from the Database.")
    message = await client.wait_for("MESSAGE",check=lambda m: m.author == ctx.author and isinstance(m.channel,nextcord.DMChannel))
    if message.content == "auth cancel":
        return await ctx.author.send("Cancelled!")
    frnt = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    config[str(ctx.author.id)] = frnt.encrypt(message.content.encode("utf-8")).decode("utf-8")
    with open("config.json","w") as f:
        json.dump(config,f)
    git = github.Github(message.content)
    user = git.get_user()
    logger.info(f"Data created for {ctx.author.name} (LINK {user.login}")
    await ctx.send(f'Logged in as {git.get_user().name}')
