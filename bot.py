from nextcord.ext import commands, tasks
import json
import nextcord
import github
import requests
from cryptography.fernet import Fernet

client = commands.Bot(command_prefix='v!')

@client.group(name="org")
async def _org(ctx):
    pass

@_org.command()
async def hook_create(ctx,org,name="Vitrealis-Autopost",url="https://webhook.site"):
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    orga = git.get_organization(org)
    
    orga.create_hook("V",config={
        'name':'Vitrealis',
        'events':[
            "push",
            "pull_request",
            'issues',
            'issue_comment'
        ],
        'config':{
            'url':url,
            'active':True
        }})

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

@client.command()
async def repo(ctx,repo_name):
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

@client.group()
async def init(ctx):
    ...

@init.command()
async def logs(ctx,repository,channel:nextcord.TextChannel,events=""):
    
    fernet = Fernet(open("key.key",'rb').read())
    with open("config.json","r") as f:
        config = json.load(f)
    if not str(ctx.author.id) in config:
        return await ctx.send(":x: You have to sync your Profile to a GitHub account: `v!init key`")
    webhooks = await channel.webhooks()
    git = github.Github(fernet.decrypt(config[str(ctx.author.id)].encode()).decode('utf-8'))
    githook = nextcord.utils.get(webhooks,name="Vitrealis")
    if not githook:
        githook = await channel.create_webhook(name="Vitrealis",avatar=await client.user.avatar.read())
    repo = git.get_repo(repository)
    await ctx.send(":information_source: Creating Webhook for Repository "+repo.name)
    repo.create_hook(name="web",config={
        'url':githook.url,
        'token':config[str(ctx.author.id)].encode().decode('utf-8')
    },events=[
            "push",
            "pull_request",
            'issues',
            'issue_comment'
        ],active=True)
    embed = nextcord.Embed(title='Webhook created!',color=nextcord.Color.dark_magenta(),description=f'A Webhook was created for {repository} by [{git.get_user().name}]({git.get_user().url})')
    await githook.send(embed=embed)

@logs.error
async def event_log_error(ctx,error):
    await ctx.send(f':x: %s' % error)

@init.command()
async def key(ctx):
    await ctx.author.send("Please enter your GitHub Auth Key or type `auth cancel` to cancel.\n\n")
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
    await ctx.send(f'Logged in as {git.get_user().name}')
