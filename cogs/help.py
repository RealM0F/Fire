import logging
from discord.ext import commands
import discord
import typing


class Help(commands.Cog):
	"""Handles the help command for Fire"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='help', description='Provides help for those who need it')
	async def help(self, ctx, item: str = None):
		cogs = []
		cmds = {}
		allcmds = False
		cmdhelp = False
		usedprefix = ctx.prefix
		if usedprefix == f'{ctx.guild.me.mention} ':
			usedprefix = '@Fire '
		if item:
			if item == 'all':
				allcmds = True
				cmdhelp = False
			else:
				cmd = self.bot.get_command(item)
				if not cmd:
					raise commands.ArgumentParsingError(f'No command called {item}')
				cmdhelp = True
		else:
			cmdhelp = False
		if not cmdhelp:
			for cog in self.bot.cogs.values():
				skip = False
				if not allcmds:
					if cog.qualified_name.lower() == 'jishaku':
						skip = True
					if cog.qualified_name.lower() == 'help':
						skip = True
					if cog.qualified_name.lower() == 'premium commands':
						premiumGuilds = cog.premiumGuilds
						if not ctx.guild.id in premiumGuilds:
							skip = True
					if cog.qualified_name.lower() == 'discordbotsorgapi':
						skip = True
					if cog.qualified_name.lower() == 'fire api':
						skip = True
				if not skip:
					cogs.append(f'**{cog.qualified_name.upper()}**')
					cmds[f'**{cog.qualified_name.upper()}**'] = []
					for cmd in cog.get_commands():
						if cmd.hidden:
							if allcmds:
								cmds[f'**{cog.qualified_name.upper()}**'].append(cmd.name)
							else:
								pass
						else:
							cmds[f'**{cog.qualified_name.upper()}**'].append(cmd.name)
					cmds[f'**{cog.qualified_name.upper()}**'] = ' - '.join(cmds[f'**{cog.qualified_name.upper()}**'])
		elif cmd:
			name = cmd.name
			desc = cmd.description
			usage = cmd.help.replace('PFX', ctx.prefix)
			embed = discord.Embed(colour=ctx.author.color)
			embed.set_author(name=f"Help has arrived for {name}!", icon_url="https://cdn.discordapp.com/avatars/444871677176709141/1b7beb893e2bf1d2a759d869e7f287dd.webp?size=1024")
			embed.add_field(name="Description", value=desc, inline=False)
			embed.add_field(name="Usage", value=usage, inline=False)
			embed.set_footer(text="<> = Required | [<>] = Optional")
			await ctx.send(embed=embed)
			return
		text = []
		for cog in cogs:
			text.append(f'{cog}\n{cmds[cog]}\n')
		embed = discord.Embed(colour=ctx.author.color, description='\n'.join(text))
		embed.set_author(name="Help has arrived!", icon_url="https://cdn.discordapp.com/avatars/444871677176709141/1b7beb893e2bf1d2a759d869e7f287dd.webp?size=1024")
		embed.set_footer(text=f"Do {usedprefix}help <command> for more information")
		await ctx.send(embed=embed)


def setup(bot):
	bot.old_help = bot.remove_command("help")
	bot.add_cog(Help(bot))


def teardown(bot):
	bot.add_command(bot.old_help)