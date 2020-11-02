def filterMessage(message, rules):
  # The rule will be like: N_N_TEXT
  # Where "N" is a number 1-9
  # First N is group of rule, second in rule option
  # And the "TEXT" is a string built in a way reffering to "N"
  newMessage = message
  hasPassed = True
  dontSend = False

  for rule in rules:
    data = rule.split('_')

    ruleCode = int(data[0])
    ruleOptionCode = int(data[1])

    ruleData = data[2]

    if ruleCode == 1:
      # word rule:
      if ruleOptionCode == 1:
        # word white list
        filterRes = wordWhiteList(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 2:
        # word black list
        filterRes = wordBlackList(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 3:
        # replace word
        filterRes = wordReplace(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 4:
        # add before
        filterRes = addBefore(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 5:
        # add after
        filterRes = addAfter(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 6:
        # clear formatting
        filterRes = clearFormatting(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']

  if dontSend == True:
    return { 'message': newMessage, 'hasPassed': False }
  else:
    return { 'message': newMessage, 'hasPassed': hasPassed }


# fuctions
def wordWhiteList(message, words):
  wordsArr = words.split(';')

  timesWordRepeated = 0

  for word in wordsArr:
    if word.lower() in message.message.lower():
      timesWordRepeated += 1

  if timesWordRepeated:
    return {'message': message, 'hasPassed': True, 'dontSend': False}
  else:
    return {'message': message, 'hasPassed': False, 'dontSend': True}

def wordBlackList(message, words):
  wordsArr = words.split(';')

  hasWords = False

  for word in wordsArr:
    if word.lower() in message.message.lower():
      hasWords = True

  if hasWords:
    return {'message': message, 'hasPassed': False, 'dontSend': True}
  else:
    return {'message': message, 'hasPassed': True, 'dontSend': False}

def wordReplace(message, data):
  listOfItems = data.split(';')

  messageText = message.message

  for item in listOfItems:
    words = item.split(':')
    word1 = words[0]
    word2 = words[1]
    messageText = messageText.replace(word1, word2)

  message.message = messageText

  return {'message': message, 'hasPassed': True, 'dontSend': False}

def addBefore(message, text):
  seperator = ''

  if text.endswith('>'):
    seperator = '\n'
    text = text[:-1]
  else:
    seperator = ' '
  
  newText = text + seperator + message.message
  
  if message.entities:
    for ent in message.entities:
      ent.offset += len(text) + 1

  message.message = newText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def addAfter(message, text):
  seperator = ''

  if text.endswith('>'):
    seperator = '\n'
    text = text[:-1]
  else:
    seperator = ' '
  
  newText = message.message + seperator + text
  
  message.message = newText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def clearFormatting(message, data):
  message.entities = []
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}