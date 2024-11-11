import discord
from discord.ext import commands
from utils.embed_wrapper import create_embed
from utils.checks import not_blacklisted
import json

class VouchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='vouch', description='Vouch for a user.')
    @not_blacklisted()
    async def vouch(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.Member, description='User who is being vouched'),
        feedback: discord.Option(str, description='Additional feedback'),
        stars: discord.Option(
            str,
            description='Feedback stars',
            choices=[
                discord.OptionChoice(name='⭐', value='⭐'),
                discord.OptionChoice(name='⭐⭐', value='⭐⭐'),
                discord.OptionChoice(name='⭐⭐⭐', value='⭐⭐⭐'),
                discord.OptionChoice(name='⭐⭐⭐⭐', value='⭐⭐⭐⭐'),
                discord.OptionChoice(name='⭐⭐⭐⭐⭐', value='⭐⭐⭐⭐⭐'),
            ],
        ),
        attachment: discord.Option(
            discord.Attachment,
            description='Attachment of the product',
            required=False,
        ),
    ):
        # Check if the vouched user is blacklisted
        if self.bot.db.is_user_blacklisted(user.id):
            embed = create_embed(
                title='Error',
                description=f'{user.mention} is blacklisted and cannot be vouched for.',
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        attachment_url = attachment.url if attachment else None

        # Store vouch in the database
        self.bot.db.add_vouch(
            vouched_user_id=user.id,
            vouched_user_name=str(user),
            feedback=feedback,
            stars=stars,
            attachment_url=attachment_url,
            vouched_by_id=ctx.author.id,
            vouched_by_name=str(ctx.author),
        )

        # Get the updated vouch count for the user
        vouch_count = self.bot.db.get_vouch_count(user.id)

        # Get embed configurations
        embed_template = self.bot.get_embed_config()
        

        # Replace placeholders in template with actual values
        placeholders = {
            'vouched_user': user.mention,
            'vouched_by': ctx.author.mention,
            'stars': stars,
            'total_vouches': str(vouch_count),
            'feedback': feedback,
            'attachment_url': attachment_url or '',
        }

        embed_title = embed_template.get('title', 'New Vouch').format(**placeholders)
        embed_description = embed_template.get('description', '').format(**placeholders)
        color_hex = embed_template.get('color', '#0000FF')
        embed_config = self.bot.get_embed_config()
        color_int = int(embed_config.get("color", "#0000FF").strip("#"), 16)
        footer_text = embed_config.get("footer", "")

        embed_footer = embed_template.get('footer', '').format(**placeholders)

        vouch_embed = discord.Embed(
            title=embed_title, description=embed_description, color=color_int
        )

        fields = embed_template.get('fields', [])
        for field in fields:
            field_name = field.get('name', '').format(**placeholders)
            field_value = field.get('value', '').format(**placeholders)
            inline = field.get('inline', True)
            vouch_embed.add_field(name=field_name, value=field_value, inline=inline)

        if embed_footer:
            vouch_embed.set_footer(text=embed_footer)

        image_url = embed_template.get('image', '').format(**placeholders)
        if image_url:
            vouch_embed.set_image(url=image_url)

        # Send the embed to the specified channel
        vouch_channel = self.bot.get_channel(self.bot.config['vouch_channel_id'])
        if vouch_channel:
            await vouch_channel.send(embed=vouch_embed)
            # Acknowledge the command
            embed = create_embed(
                title='Vouch Submitted',
                description='Your vouch has been submitted successfully.',
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                title='Error',
                description='Vouch channel not found. Please contact an administrator.',
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(VouchCog(bot))
