import discord
from discord.ext import commands
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import aiosqlite3
import functools
import datetime
import asyncio
import json
import os

print("Premium functions have been loaded!")

with open('config.json', 'r') as cfg:
	config = json.load(cfg)

def isadmin(ctx):
	"""Checks if the author is an admin"""
	if str(ctx.author.id) not in config['admins']:
		admin = False
	else:
		admin = True
	return admin

class Premium(commands.Cog, name="Premium Commands"):
	def __init__(self, bot):
		self.bot = bot
		self.loop = bot.loop

	async def cog_check(self, ctx: commands.Context):
		"""
		Local check, makes all commands in this cog premium only
		"""
		if await self.bot.is_owner(ctx.author):
			return True
		await ctx.bot.db.execute(f'SELECT * FROM premium WHERE gid = {ctx.guild.id};')
		premium = await ctx.bot.db.fetchone()
		if premium != None:
			return True
		else:
			return False

	async def member_guild_check(self, member: discord.Member):
		"""
		Check if the guild from a member is premium
		"""
		if await self.bot.is_owner(member):
			return True
		await self.bot.db.execute(f'SELECT * FROM premium WHERE gid = {member.guild.id};')
		premium = await self.bot.db.fetchone()
		if premium != None:
			return True
		else:
			return False

	def gencrabrave(self, t, filename):
		clip = VideoFileClip("crabtemplate.mp4")
		text = TextClip(t[0], fontsize=48, color='white', font='Verdana')
		text2 = TextClip("____________________", fontsize=48, color='white', font='Verdana')\
			.set_position(("center", 210)).set_duration(15.4)
		text = text.set_position(("center", 200)).set_duration(15.4)
		text3 = TextClip(t[1], fontsize=48, color='white', font='Verdana')\
			.set_position(("center", 270)).set_duration(15.4)

		video = CompositeVideoClip([clip, text.crossfadein(1), text2.crossfadein(1), text3.crossfadein(1)]).set_duration(15.4)

		video.write_videofile(filename, threads=25, preset='superfast', verbose=False)
		clip.close()
		video.close()

	@commands.command(name='crabrave', description='Make a Crab Rave meme!', hidden=True)
	async def crabmeme(self, ctx, *, text: str):
		'''Limited to owner only (for now, it may return) due to this command using like 90% CPU'''
		if not await self.bot.is_owner(ctx.author):
			return
		if not '|' in text:
			raise commands.ArgumentParsingError('Text should be separated by |')
		if not text:
			raise commands.MissingRequiredArgument('You need to provide text for the meme')
		filename = str(ctx.author.id) + '.mp4'
		t = text.upper().replace('| ', '|').split('|')
		if len(t) != 2:
			raise commands.ArgumentParsingError('Text should have 2 sections, separated by |')
		if (not t[0] and not t[0].strip()) or (not t[1] and not t[1].strip()):
			raise commands.ArgumentParsingError('Cannot use an empty string')
		msg = await ctx.send('🦀 Generating Crab Rave 🦀')
		await self.loop.run_in_executor(None, func=functools.partial(self.gencrabrave, t, filename))
		meme = discord.File(filename, 'crab.mp4')
		await msg.delete()
		await ctx.send(file=meme)
		os.remove(filename)

	@commands.command(name='autorole', description='Automatically add a role to a user when they join')
	async def autorole(self, ctx, role: discord.Role = None):
		'''PFXautorole [<role name/id/mention>]\nUse command without role argument to disable'''
		await self.bot.db.execute(f'SELECT * FROM settings WHERE gid = {ctx.guild.id}')
		guildsettings = await self.bot.db.fetchone()
		if guildsettings == None:
			await self.bot.db.execute(f'INSERT INTO settings (\"gid\") VALUES ({ctx.guild.id});')
			await self.bot.conn.commit()
		if not role:
			await self.bot.db.execute(f'UPDATE settings SET autorole = 0 WHERE gid = {ctx.guild.id}')
			await self.bot.conn.commit()
			return await ctx.send(f'Successfully disabled auto-role in {ctx.guild.name}', delete_after=5)
		else:
			roleid = role.id
			await self.bot.db.execute(f'UPDATE settings SET autorole = {role.id} WHERE gid = {ctx.guild.id}')
			await self.bot.conn.commit()
			return await ctx.send(f'Successfully enabled auto-role in {ctx.guild.name}! All new members will recieve the {role.name} role.', delete_after=5)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if await self.member_guild_check(member):
			await self.bot.db.execute(f'SELECT autorole FROM settings WHERE gid = {member.guild.id};')
			role = await self.bot.db.fetchone()
			try:
				role = discord.utils.get(member.guild.roles, id=role[0])
			except Exception:
				return
			if role != None:
				await member.add_roles(role, reason='Auto-Role')
			

def setup(bot):
	bot.add_cog(Premium(bot))