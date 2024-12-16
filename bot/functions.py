from bot.env import user_cache, users, items, special_user
import discord


async def create_embed(list_elements, list_len, page, selected=None, per_page=5):
    start = page * per_page
    end = start + per_page
    embed = discord.Embed(title=f"Page {page + 1}")
    for i, item in enumerate(list_elements[start:end]):
        if i == selected:
            item = f"***    {item} ***"
        embed.add_field(name=item, value="\u200b", inline=False)
    embed.set_footer(text=f"Page {page + 1} / {(list_len + per_page - 1) // per_page}")
    return embed


def get_embed_position(reaction_emoji, page, selected, list_len=20, per_page=5):
    if str(reaction_emoji) == "⬅️":
        if page > 0:
            page -= 1
            selected = 0
    elif str(reaction_emoji) == "➡️":
        if page < (list_len - 1) // per_page:
            page += 1
            selected = 0
    elif str(reaction_emoji) == "🔼":
        if selected > 0:
            selected -= 1
    elif str(reaction_emoji) == "🔽":
        if selected < min(per_page - 1, list_len - 1):
            selected += 1

    return page, selected


def special_phrase(phrase, user_id):
    if user_id == special_user[0]:
        phrase += special_user[1]
    return phrase


def create_user(discord_id, username, set_channel=None):
    user = {
        "discord_id": discord_id,
        "username": username,
        "set_channel": set_channel
    }
    users.insert_one(user)


def create_item(name, parent_id, owner_id, channel_id, message_id):
    item = {
        "name": name,
        "parent_id": parent_id,
        "owner_id": owner_id,
        "channel_id": channel_id,
        "message_id": message_id
    }
    items.insert_one(item)


def check_user(discord_id):
    return users.find_one({"discord_id": discord_id}) is not None


def get_item(name, owner_id):
    query = {"name": name, "owner_id": owner_id}
    projection = {"_id": 1, "message_id": 1, "channel_id": 1}
    item = items.find_one(query, projection)
    return item


def get_children(folder_name, user):
    query_folder = {"name": folder_name, "owner_id": user}
    folder = items.find_one(query_folder)
    if folder["message_id"] is not None or folder is None:
        return []

    query_children = {"parent_id": folder["_id"], "owner_id": user}
    children = list(items.find(query_children))
    children = [child for child in children if child["message_id"] is not None]

    return children


def rename_file(file_name, new_name, user):
    query_new_name = {"name": new_name, "owner_id": user}
    new_name_id = items.find_one(query_new_name, {"_id": 1})
    if new_name_id is not None:
        return False

    query_name = {"name": file_name, "owner_id": user}
    name_id = items.find_one(query_name, {"_id": 1})
    if name_id is None:
        return False

    update = {"$set": {"name": new_name}}
    result = items.update_one(query_name, update)
    return result.modified_count > 0


def update_set_channel(channel_id, user_id):
    query = {"discord_id": user_id}
    update = {"$set": {"set_channel": channel_id}}
    result = users.update_one(query, update)
    return result.modified_count > 0


def get_set_chanel(user_id):
    query = {"discord_id": user_id}
    projection = {"_id": 0, "set_channel": 1}
    user = users.find_one(query, projection)
    return user["set_channel"]

def update_parent(message_name, folder_name, user):
    if folder_name is None:
        parent_id = None
    else:
        query_folder = {"name": folder_name, "owner_id": user}
        folder = items.find_one(query_folder, {"_id": 1, "parent_id": 1})
        if folder is None:
            return False
        parent_id = folder["_id"]

    query_name = {"name": message_name, "owner_id": user}
    name_id = items.find_one(query_name, {"_id": 1})
    if name_id is None:
        return False
    name_id = name_id["_id"]

    current_id = parent_id
    while current_id:
        if current_id == name_id:
            return False
        current_query = {"_id": current_id, "owner_id": user}
        projection = {"_id": 0, "parent_id": 1}
        current_item = items.find_one(current_query, projection)
        current_id = current_item["parent_id"]

    update = {"$set": {"parent_id": parent_id}}
    result = items.update_one(query_name, update)

    return result.modified_count > 0


def delete_descendants(node_id):
    children = items.find({"parent_id": node_id})
    for child in children:
        delete_descendants(child["_id"])
    items.delete_one({"_id": node_id})


def delete_node(message_name, user):
    query_name = {"name": message_name, "owner_id": user}
    node_id = items.find_one(query_name, {"_id": 1})

    if node_id is None:
        return False
    node_id = node_id["_id"]

    delete_descendants(node_id)

    return items.find_one({"_id": node_id})


def duplicate_descendants(node_id, target_id, message_append, parent_id=None):
    if parent_id is None:
        children = items.find({"_id": node_id})
    else:
        children = items.find({"parent_id": node_id})

    for child in children:
        child_copy = child.copy()

        child_copy["owner_id"] = target_id
        child_copy["parent_id"] = parent_id
        child_copy["name"] = child_copy["name"] + message_append

        child_copy.pop('_id', None)

        new_node_id = items.insert_one(child_copy).inserted_id
        duplicate_descendants(child["_id"], target_id, message_append, new_node_id)


def set_nodes(message_name, owner_id, target_id, message_append):
    query_name = {"name": message_name, "owner_id": owner_id}
    node = items.find_one(query_name)

    if node is None:
        return False

    duplicate_descendants(node["_id"], target_id, message_append)

    return True


def search_descendants(node_id, target_id, append_name):
    children = items.find({"parent_id": node_id})
    for child in children:
        if not search_descendants(child["_id"], target_id, append_name):
            return False
    node = items.find_one({"_id": node_id})
    item = get_item(node["name"] + append_name, target_id)
    if item:
        return False
    return True


def search_node(name, owner_id, target_id, append_name):
    node = get_item(name, owner_id)
    if not node:
        return False
    node_id = node["_id"]
    return search_descendants(node_id, target_id, append_name)


async def get_list(owner_id, folder_name=None):
    parent_id = None
    if folder_name is not None:
        query = {"name": folder_name, "owner_id": owner_id}
        folder = items.find_one(query, {"_id": 1})
        parent_id = folder["_id"]

    query = {"owner_id": owner_id, "parent_id": parent_id}
    owner_items = items.find(query)

    names = []
    for owner_item in owner_items:
        if 'name' in owner_item:
            if owner_item['message_id'] is not None:
                name = "📃 "
            else:
                name = "📁 "
            names.append(name + owner_item['name'])

    names = sorted(names)
    return 0, 0, names, len(names)


async def cache_list(owner_id, folder_name=None):
    if owner_id not in user_cache:
        data = await get_list(owner_id, folder_name)
        user_cache[owner_id] = data

    cached_list = user_cache[owner_id]
    return cached_list


async def delete_cache(owner_id):
    if owner_id in user_cache:
        del user_cache[owner_id]
        return True

    return False


async def update_cache(owner_id, reaction):
    page, selected, list_elements, list_len = await cache_list(owner_id)
    page, selected = get_embed_position(reaction, page, selected, list_len)
    user_cache[owner_id] = (page, selected, list_elements, list_len)
    return user_cache[owner_id]


async def get_item_data(name: str, user_id: int):
    try:
        item = get_item(name, user_id)
        if not item:
            raise ValueError("Item not found")
        return item
    except Exception as e:
        raise e


async def fetch_message(item, b):
    try:
        channel = b.get_channel(item["channel_id"]) or await b.fetch_channel(item["channel_id"])
        if channel is None:
            raise ValueError("No access to channel")

        message = await channel.fetch_message(item["message_id"])

        if message.attachments:
            image_urls = [attachment.url for attachment in message.attachments if
                          attachment.content_type and 'image' in attachment.content_type]
            return {"message": message, "images": image_urls}

        return {"message": message, "images": []}
    except discord.NotFound:
        raise discord.NotFound('Message not found.')
    except discord.Forbidden:
        raise discord.Forbidden('Forbidden access.')
    except discord.HTTPException:
        raise discord.HTTPException('HTTP operation failed.')


async def send_message_and_embed_images(interaction, message_data, bot=None):
    message = message_data["message"]
    images = message_data["images"]

    URL = 'https://www.google.com/'
    embeds = []
    temp = None
    for image_url in images:
        if temp is None:
            temp = discord.Embed(url=URL)

        embed = temp.copy()
        embed.set_image(url=image_url)
        embeds.append(embed)

    channel_id = get_set_chanel(interaction.user.id)
    if channel_id is not None:
        channel = bot.get_channel(channel_id)
        if channel is not None:
            await channel.send(content=message.content, embeds=embeds)
            return

    if not interaction.response.is_done():
        await interaction.response.send_message(content=message.content, embeds=embeds)
    else:
        await interaction.followup.send(content=message.content, embeds=embeds)