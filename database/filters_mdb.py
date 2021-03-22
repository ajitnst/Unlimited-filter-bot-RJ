import os
import re
import pymongo

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
 
myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.DATABASE_NAME]



async def add_filter(grp_id, text, reply_text, btn, file):
    mycol = mydb[str(grp_id)]

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        print('Couldnt save, check your db')
             
     
async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    
    query = mycol.find( {"text":name})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            file = file['file']
        return reply_text, btn, file
    except:
        return None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_fil(message, text, group_id):
    mycol = mydb[str(group_id)]
    
    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that filter anymore.",
            quote=True,
            parse_mode="md"
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.reply_text(f"Nothing to remove in {title}!", quote=True)
        return
        
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.reply_text(f"All filters from {title} has been removed", quote=True)
    except:
        await message.reply_text(f"Couldn't remove all filters from group!", quote=True)
        return


async def countfilters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    if count == 0:
        return False
    else:
        return count


async def allfilters():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    if "USERS" in collections:
        collections.remove("USERS")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount = totalcount + count

    totalcollections = len(collections)

    return totalcollections, totalcount