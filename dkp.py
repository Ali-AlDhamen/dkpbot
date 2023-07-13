import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import discord
from discord.ext import commands
from secret import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

cred = credentials.Certificate(firebase_configuration)
firebase_admin.initialize_app(cred)
db = firestore.client()


@bot.event
async def on_ready():
    print('bot is ready.')



@bot.command()
async def create(ctx, arg):
    role = "developer"
    if role in [y.name.lower() for y in ctx.author.roles]:
        doc_ref = db.collection("users").document(arg)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({
                'name': arg,
                'dkp': 0
            })
            await ctx.send(f'User {arg} created. with 0 dkp')
        else:
            await ctx.send(f'User {arg} already exists')
    else:
        await ctx.send('you are not allowed to do that only developers can do that')




@bot.command()
async def remove(ctx, arg1, arg2):
    doc_ref = db.collection("users").document(arg1)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            'dkp': doc.to_dict()['dkp'] - int(arg2)
        })
        await ctx.send(f'{arg2} dkp removed from {arg1}')
    else:
        await ctx.send(f'User {arg1} not found')


@bot.command()
async def dkp(ctx, arg):
    doc_ref = db.collection("users").document(arg)
    doc = doc_ref.get()
    if doc.exists:
        await ctx.send(f'{arg} has {doc.to_dict()["dkp"]} dkp')
    else:
        await ctx.send(f'User {arg} not found')


@bot.command()
async def list(ctx):
    users_ref = db.collection("users")
    docs = users_ref.stream()
    msg = ''
    for doc in docs:
        msg += f'{doc.to_dict()["name"]} has {doc.to_dict()["dkp"]} dkp\n'
    await ctx.send(msg)


@bot.command()
async def add(ctx, amount, *args):
    users_ref = db.collection("users")
    docs = users_ref.stream()
    msg = f'{amount} dkp added!'
    users = list(args)

    for doc in docs:
        if doc.to_dict()['name'] in args:
            doc.reference.update({
                'dkp': doc.to_dict()['dkp'] + int(amount)
            })
            users.remove(doc.to_dict()['name'])

    if len(users) > 0:
        error_message = 'except the following users:\n'
        for user in users:
            error_message += f'user {user} not found\n'
        await ctx.send(msg)
        await ctx.send(error_message)
    else:        
        await ctx.send(msg)

bot.remove_command('help')


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="DKP Bot", description="DKP Bot for discord", color=0xeee657)

    embed.add_field(name="Author", value="Ali")
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # explain the commands
    embed.add_field(name="!create <name>",
                    value="create a new user with 0 dkp (admin only)")
    embed.add_field(name="!remove <name> <amount>",
                    value="remove dkp from a user")
    embed.add_field(name="!dkp <name>", value="show dkp of a user")
    embed.add_field(name="!list", value="list all users and their dkp")
    embed.add_field(name="!add <amount> <name1> <name2> ...",
                    value="add dkp to multiple users")
    embed.add_field(name="!addboss <name> <amount>",
                    value="create a new boss with dkp (admin only)")
    embed.add_field(name="!removeboss <name>",
                    value="remove a boss (admin only)")
    embed.add_field(name="!boss <name>", value="show dkp of a boss")
    embed.add_field(name="!listbosses", value="list all bosses and their dkp")
    embed.add_field(name="!addboss <bossname> <name1> <name2> ...",
                    value="add boss dkp to multiple users")

    embed.add_field(name="!help", value="show this message")

    await ctx.send(embed=embed)


@bot.command()
async def addboss(ctx, arg1, arg2):
    role = "developer"
    arg1 = arg1.lower()
    if role in [y.name.lower() for y in ctx.author.roles]:
        doc_ref = db.collection("bosses").document(arg1)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({
                'name': arg1,
                'dkp': int(arg2)
            })
            await ctx.send(f'boss {arg1} created. with {arg2} dkp')
        else:
            await ctx.send(f'boss {arg1} already exists')
    else:
        await ctx.send('you are not allowed to do that, only developers can do that')


@bot.command()
async def removeboss(ctx, arg1):
    role = "developer"
    arg1 = arg1.lower()
    if role in [y.name.lower() for y in ctx.author.roles]:
        doc_ref = db.collection("bosses").document(arg1)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            await ctx.send(f'boss {arg1} deleted.')
        else:
            await ctx.send(f'boss {arg1} not found')
    else:
        await ctx.send('you are not allowed to do that, only developers can do that')


@bot.command()
async def boss(ctx, arg):
    arg = arg.lower()
    doc_ref = db.collection("bosses").document(arg)
    doc = doc_ref.get()
    if doc.exists:
        await ctx.send(f'{arg} has {doc.to_dict()["dkp"]} dkp')
    else:
        await ctx.send(f'boss {arg} not found')


@bot.command()
async def listbosses(ctx):
    users_ref = db.collection("bosses")
    docs = users_ref.stream()
    if len(docs) == 0:
        await ctx.send('no bosses found')
    msg = ''
    for doc in docs:
        msg += f'{doc.to_dict()["name"]} has {doc.to_dict()["dkp"]} dkp\n'
    await ctx.send(msg)


@bot.command()
async def addboss(ctx, arg1, *args):
    arg1 = arg1.lower()
    doc_ref = db.collection("bosses").document(arg1)
    boss_doc = doc_ref.get()
    if doc.exists:
        users_ref = db.collection("users")
        docs = users_ref.stream()
        msg = f'{arg1} dkp added!'
        users = list(args)

        for doc in docs:
            if doc.to_dict()['name'] in args:
                doc.reference.update({
                    'dkp': doc.to_dict()['dkp'] + int(boss_doc.to_dict()['dkp'])
                })
                users.remove(doc.to_dict()['name'])

        if len(users) > 0:
            error_message = 'except the following users:\n'
            for user in users:
                error_message += f'user {user} not found\n'
            await ctx.send(msg)
            await ctx.send(error_message)
        else:
            await ctx.send(msg)




            
bot.run(bot_token)
