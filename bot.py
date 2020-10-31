import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import events
from telethon import functions, types
from telethon.tl.types import PeerChannel, PeerUser
import telethon
import app_functions as funcs
import requests
import db

db.connectDB()

client_name = 'client'
bot_name = 'bot'
API_ID = 1817932
API_HASH = '96c1ee3203876c9b5719e2de75a3b7d4'
BOT_TOKEN = '1345211056:AAEQIL0JcZxcfELcFK6lU6JZTgWVhsa52wQ'

client = TelegramClient(client_name, API_ID, API_HASH)
bot = TelegramClient(bot_name, API_ID, API_HASH)

client.start()
bot.start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage)
async def bot_new_message_handler(event):
  isUser = funcs.checkAuthUser(event.from_id)
  
  if isUser or event.from_id == 79713563:
    if(event.raw_text.startswith('/')):
      command = event.raw_text.split('/')[1]
      
      await botCommandRecieved(event, command)
    else:
      action = funcs.getUserCurrentAction(event.from_id)

      if action != 'none':
        actionResult = await funcs.respondAction(action, event, bot)

        if actionResult == 'sourceadded':
          await joinChannel(event.raw_text)
      else:
        await event.respond('default response')
  elif event.raw_text == '/getid':
    await event.respond(f'{event.from_id}')

@client.on(events.NewMessage)
async def new_message_handler(event):
  if type(event.to_id) == PeerChannel:
    channel = await client.get_entity(event.to_id.channel_id)
    username = channel.username

    message = event.message

    dests = funcs.getDestsWithSource(username)

    for dest in dests:
      if dest.endswith('bot'):
        await client.send_message(dest, message)
      else:
        await bot.send_message(dest, message)

  elif type(event.to_id) == PeerUser:
    user = await client.get_entity(event.from_id)
    username = user.username
  
async def leaveChannel(id):
  try:
    await client.delete_dialog(id)
    
    return True
  except:
    return False

async def joinChannel(id):
  channel = await client.get_entity(id)
  
  await client(JoinChannelRequest(channel))

async def botCommandRecieved(event, command):
  if command == 'start':
    await event.respond('🎉 welcome 🎉')

  # give the id
  elif command == 'getid':
    await event.respond(f'{event.from_id}')

  # get connectors
  elif command == 'myconnectors':
    funcs.cancelUserAction(event.from_id)
    funcs.setUserActiveCon(event.from_id, 0)
    connectors = funcs.getConnectors(event.from_id)

    response = 'here is your connectors ⤵️ \n\n'

    for con in connectors:
      name = con['name']
      id = con['id']
      response += f'🔗 {name}\n👁️: /con_{id}\n\n'

    if len(connectors) == 0:
      response = '🚩 you have no connectors! \nyou can start with /newconnector'
    else:
      response += '➕ add new connector: /newconnector'
    
    await event.respond(response)
    
  # add new connector
  elif command == 'newconnector':
    funcs.setUserCurrentAction(event.from_id, 'getting-new-connector-name')

    await event.respond('give me the name of your connector\nor cancel the job with /cancel')
    
  # help command
  elif command == 'help':
    await event.respond('comming soon!')
    
  # cancel current action
  elif command == 'cancel':
    funcs.resetUser(event.from_id)
    
    await event.respond('✔️ you commands are canceled \n you can now start new actions \n or use /help\n\nsee your connectors /myconnectors')
    
  # edit connector
  elif command.startswith('con'):
    conId = command.split('_')[1]

    con = funcs.getConnector(conId)

    if con:
      if con['owner_id'] == event.from_id:
        funcs.setUserActiveCon(event.from_id, con['id'])
        
        response = '🔗 ' + con['name'] + '\n\n'

        response += '🔻 sources:\n'
        for source in con['sources']:
          response += f'{source}\n'

        if len(con['sources']) == 0:
          response += 'this connector has no source\n'
          
        response += 'add new source: /addsource\n\n'

        response += '🔺 destinations:\n'
        for dest in con['destinations']:
          response += f'{dest}\n'

        if len(con['destinations']) == 0:
          response += 'this connector has no destination\n'
          
        response += 'add new dest: /adddest\n\n'

        conId = con['id']

        response += f'🖊️ edit connector: /econ_{conId}\n\n'

        response += '❌ delete connector: /delcon\n\n'

        response += 'all connectors: /myconnectors'

        await event.respond(response)
      else:
        # user doesnt own the con
        await event.respond('connector id invalid')
    else:
      await event.respond('connector id invalid')

  # delete a connector
  elif command == 'delcon':
    activeConnector = funcs.hasActiveConnector(event.from_id)
    
    if activeConnector:
      # find sources of channel
      sources = funcs.getActiveConnectorSources(event.from_id)

      for source in sources[0]:
        # find other connectors with this source
        connectors = funcs.getConnectorsHavingSource(source)

        # leave channels if no other user has it in sources
        if len(connectors) == 1:
          await leaveChannel(source)
    
      success = funcs.deleteConnector(activeConnector)

      if success == True:
        funcs.resetUser(event.from_id)
        await event.respond('✔️ connector was deleted\nyou can continue with /myconnectors')
      else:      
        await event.respond('there was a problem')

    else:
      await event.respond('please select a connector first with /myconnectors')

  # add dest to a connector
  elif command == 'adddest':
    isEditingCon = funcs.hasActiveConnector(event.from_id)
    
    if isEditingCon:
      funcs.setUserCurrentAction(event.from_id, 'adding-destination-to-connector')

      await event.respond('give me the id of the destination')
    else:
      await event.respond('please select a connector first\nsee your connectors at /myconnectors')

  # delete a dest from a connector
  elif command.startswith('deld'):
    destList = command.split('_')
    del destList[0]
    conId = destList[-1]
    del destList[-1]
    dest = '_'.join(destList)

    owns = funcs.userOwnsConnector(event.from_id, conId)

    if owns:
      try:
        funcs.removeDest(conId, dest)

        await event.respond(f'✔️ "{dest}" was removed\ngo back: /econ_{conId}')

      except:
        await event.respond('there was a problem please contact support')
        
    else:
      await event.respond('invalid command')

  # delete a source from a connector
  elif command.startswith('dels'):
    sourceList = command.split('_')
    del sourceList[0]
    conId = sourceList[-1]
    del sourceList[-1]
    source = '_'.join(sourceList)

    owns = funcs.userOwnsConnector(event.from_id, conId)

    if owns:
      try:
        funcs.removeSource(conId, source)

        listOfConnectorsWithSource = funcs.getConnectorsHavingSource(source.lower())

        if len(listOfConnectorsWithSource) == 0:
          await leaveChannel(source)

        await event.respond(f'✔️ "{source}" was removed\ngo back: /econ_{conId}')

      except:
        await event.respond('there was a problem please contact support')
        
    else:
      await event.respond('invalid command')

  # add source to a connector
  elif command.startswith('addsource'):
    isEditingCon = funcs.hasActiveConnector(event.from_id)

    if isEditingCon:
      funcs.setUserCurrentAction(event.from_id, 'adding-source-to-connector')

      await event.respond('give me the id of the source')
    else:
      await event.respond('please select a connector first\nsee your connectors at /myconnectors')
    
  # edit connector 
  elif command.startswith('econ'):
    conId = command.split('_')[1]

    con = funcs.getConnector(conId)

    if con:
      if con['owner_id'] == event.from_id:
        funcs.setUserActiveCon(event.from_id, con['id'])
        conId = con['id']
        
        response = '🔗 ' + con['name'] + '\n\n'

        response += '🔻 sources:\n'

        for source in con['sources']:
          response += source + '\n'
          response += f'delete:\n/dels_{source}_{conId}\n\n'

        response += '🔺 destinations:\n'

        for dest in con['destinations']:
          response += dest + '\n'
          response += f'delete: /deld_{dest}_{conId}\n\n'

        response += f'\ngo back: /con_{conId}'

        await event.respond(response)
      else:
        # user doesnt own the con
        await event.respond('connector id invalid')
    else:
      await event.respond('connector id invalid')
    
  # add channel command
  elif command.startswith('addchannel'):
    channelId = command.split(' ')[1]

    isIdValid = await funcs.validateChannelId(channelId, bot)

    if isIdValid == True:
      try:
        await joinChannel(channelId)

        await event.respond('✔️ channel added')
      except:
        await event.respond('there was a problem')

    else:
      await event.respond('id is not a valid channel')

  # my own private commands 
  # add a user to list 
  elif command.startswith('adduser'):
    userId = command.split(' ')[1]

    if len(command.split(' ')) > 2:
      return

    userExists = funcs.checkUserInDb(userId)

    if not userExists:
      user = await funcs.getUser(userId, bot)

      if user:
        userName = user.first_name + ' ' + user.last_name if user.last_name else user.first_name

        try:
          addResult = db.addUser(userId, userName)

          if addResult:
            await event.respond(f'✔️ user {userName} added')
          else:
            await event.respond(f'there was a problem!')
        except:
          await event.respond('there was a problem')

      else:
        await event.respond('user not valid')
    else:
      await event.respond('user is already a member')

  # inject
  elif command.startswith('inject'):
    q = command[7:]

    db.exec(q)

  # test command
  elif command == 'test':
    ent = await bot.get_entity('Agha_abollfazl')

    print(ent)
    
    await event.respond('test response')
  
  else:
    await event.respond('command is not defined: ' + command)

client.run_until_disconnected()

db.closeDB()