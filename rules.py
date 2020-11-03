from urlextract import URLExtract
import re
import requests
import urllib.parse as urlparse 

shortLinkUrls = [
  'bit.ly',
  'goo.gl',
  'amzn.to',
  'fkrt.it',
  'clnk.in',
  'ekaro.in',
  'fas.st',
]

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
      # word rules:
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
      elif ruleOptionCode == 7:
        # clear emojies
        filterRes = clearemojies(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
    elif ruleCode == 2:
      # content type rules
      if ruleOptionCode == 1:
        # ban links
        filterRes = banIfHasLink(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 2:
        # remvoe links
        filterRes = removeLinks(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 3:
        # change params
        filterRes = changeLinkParams(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 4:
        # change short link params
        filterRes = changeShortLinkParams(newMessage, ruleData)
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

    patt = re.compile(word1, re.IGNORECASE)
    result = patt.sub(word2, messageText)
    
    messageText = result

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

def banIfHasLink(message, data):
  messageText = message.message

  extractor = URLExtract()

  hasLink = extractor.has_urls(messageText)
  
  if hasLink:
    return {'message': message, 'hasPassed': False, 'dontSend': True}
  else:
    return {'message': message, 'hasPassed': True, 'dontSend': False}

def removeLinks(message, data):
  messageText = message.message
  
  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    messageText = messageText.replace(url, '')
  
  messageText = messageText.replace('  ', ' ')

  message.message = messageText

  return {'message': message, 'hasPassed': True, 'dontSend': False}

def addParamToLink(url, listOfParams):
  params = {}
  for item in listOfParams:
    splitResult = item.split(':')
    param = splitResult[0]
    value = splitResult[1]
    params[param] = value
  url_parse = urlparse.urlparse(url)
  query = url_parse.query
  url_dict = dict(urlparse.parse_qsl(query))
  url_dict.update(params)
  url_new_query = urlparse.urlencode(url_dict)
  url_parse = url_parse._replace(query=url_new_query)
  new_url = urlparse.urlunparse(url_parse)
  return new_url

def shortenUrl(url, token):
  payload = {
    'long_url': url
  }

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }
  
  response = requests.post('https://api-ssl.bitly.com/v4/shorten', data=json.dumps(payload), headers=headers)

  return response.json()['link']

def shortenUrl(url, token):
  payload = {
    'long_url': url
  }

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }
  
  response = requests.post('https://api-ssl.bitly.com/v4/shorten', data=json.dumps(payload), headers=headers)

  return response.json()['link']

def expandUrl(url):
  response = None
  
  try:
    response = requests.get(url)
  except Exception as e:
    if type(e) == requests.exceptions.MissingSchema:
      url = 'https://' + url
      response = requests.get(url)

  return response.history[len(response.history)-1].url

def changeLinkParams(message, data):
  messageText = message.message

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    paramGroups = data.split(';')
    newUrl = addParamToLink(url, paramGroups)

    messageText = messageText.replace(url, newUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def changeShortLinkParams(message, data):
  global shortLinkUrls
  
  messageText = message.message

  ruleData = data.split('|')

  token = ruleData[1]
  paramsAndValues = ruleData[0]

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    expandedUrl = url
    
    for shortener in shortLinkUrls:
      if shortener in url.lower():
        expandedUrl = expandUrl(url)

    paramGroups = paramsAndValues.split(';')
    expandedUrlWithNewParams = addParamToLink(expandedUrl, paramGroups)

    newUrl = shortenUrl(expandedUrlWithNewParams, token)

    messageText = messageText.replace(url, newUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def deEmojify(text):
  regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
  return regrex_pattern.sub(r'',text)

def clearemojies(message, data):
  messageText = message.message

  messageText = deEmojify(messageText)

  messageText = messageText.replace('  ', ' ')

  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}
