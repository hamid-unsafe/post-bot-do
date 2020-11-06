from urlextract import URLExtract
import pycurl
import re
import json
import requests
import urllib.parse as urlparse 
from urllib.parse import parse_qs

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
        filterRes = wordWhiteListRule(newMessage, ruleData)
        newMessage = filterRes['1message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 2:
        # word black list
        filterRes = wordBlackListRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 3:
        # replace word
        filterRes = wordReplaceRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 4:
        # add before
        filterRes = addBeforeRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 5:
        # add after
        filterRes = addAfterRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 6:
        # clear formatting
        filterRes = clearFormattingRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 7:
        # clear emojies
        filterRes = clearemojiesRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
    elif ruleCode == 2:
      # content type rules
      if ruleOptionCode == 1:
        # ban links
        filterRes = banIfHasLinkRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 2:
        # remvoe links
        filterRes = removeLinksRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 3:
        # change params
        filterRes = changeLinkParamsRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 4:
        # change short link params
        filterRes = changeShortLinkParamAndShortenRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 5:
        # expand links
        filterRes = expandLinksRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 6:
        # shorten link
        filterRes = shortenLinksRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 7:
        # change params then shorten
        filterRes = changeParamsAndShortenLinkRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']
      elif ruleOptionCode == 8:
        # ronkovalley
        filterRes = ronkovalleyLinkRule(newMessage, ruleData)
        newMessage = filterRes['message']
        hasPassed = filterRes['hasPassed']
        if filterRes['dontSend']:
          dontSend = filterRes['dontSend']

  if dontSend == True:
    return { 'message': newMessage, 'hasPassed': False }
  else:
    return { 'message': newMessage, 'hasPassed': hasPassed }


# fuctions
def wordWhiteListRule(message, words):
  wordsArr = words.split(';')

  timesWordRepeated = 0

  for word in wordsArr:
    if word.lower() in message.message.lower():
      timesWordRepeated += 1

  if timesWordRepeated:
    return {'message': message, 'hasPassed': True, 'dontSend': False}
  else:
    return {'message': message, 'hasPassed': False, 'dontSend': True}

def wordBlackListRule(message, words):
  wordsArr = words.split(';')

  hasWords = False

  for word in wordsArr:
    if word.lower() in message.message.lower():
      hasWords = True

  if hasWords:
    return {'message': message, 'hasPassed': False, 'dontSend': True}
  else:
    return {'message': message, 'hasPassed': True, 'dontSend': False}

def wordReplaceRule(message, data):
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

def addBeforeRule(message, text):
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

def addAfterRule(message, text):
  seperator = ''

  if text.endswith('>'):
    seperator = '\n'
    text = text[:-1]
  else:
    seperator = ' '
  
  newText = message.message + seperator + text
  
  message.message = newText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def clearFormattingRule(message, data):
  message.entities = []
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def banIfHasLinkRule(message, data):
  messageText = message.message

  extractor = URLExtract()

  hasLink = extractor.has_urls(messageText)
  
  if hasLink:
    return {'message': message, 'hasPassed': False, 'dontSend': True}
  else:
    return {'message': message, 'hasPassed': True, 'dontSend': False}

def removeLinksRule(message, data):
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
    if item.endswith('?'):
      item = item[:-1]
      splitResult = item.split(':')
      param = splitResult[0]
      value = splitResult[1]
      if param in url:
        params[param] = value
    else:
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
  payload = None
  if url.startswith('http'):
    payload = {
      'long_url': url
    }
  else:
    payload = {
      'long_url': 'http://' + url
    }
  
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }
  
  response = None
  
  response = requests.post('https://api-ssl.bitly.com/v4/shorten', data=json.dumps(payload), headers=headers)

  return response.json()['link']

def expandUrl(url):
  newUrl = url

  for shortUrl in shortLinkUrls:
    if shortUrl in url:
      if True:
        retrieved_headers = Storage()

        c = pycurl.Curl()
        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(c.URL, url)
        c.setopt(c.HEADERFUNCTION, retrieved_headers.store)
        c.perform()
        c.close()
        location = retrieved_headers.location
        if 'tracking.earnkaro.com' in location:
          parsed = urlparse.urlparse(location)
          newUrl = parse_qs(parsed.query)['dl'][0]
        else:
          newUrl = location
  
  return newUrl

class Storage:
  def __init__(self):
    self.contents = ''
    self.location = ''
    self.line = 0

  def store(self, buf):
    if str(buf)[2:-5].lower().startswith('location'):
      self.location = str(buf)[12:-5]
    self.line = self.line + 1
    self.contents = "%s%i: %s" % (self.contents, self.line, buf)

  def __str__(self):
    return str(self.contents)

def changeLinkParamsRule(message, data):
  messageText = message.message

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    paramGroups = data.split(';')
    newUrl = addParamToLink(url, paramGroups)

    messageText = messageText.replace(url, newUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def changeShortLinkParamAndShortenRule(message, data):
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

def clearemojiesRule(message, data):
  messageText = message.message

  messageText = deEmojify(messageText)

  messageText = messageText.replace('  ', ' ')

  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def expandLinksRule(message, data):
  messageText = message.message

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    expandedUrl = expandUrl(url)

    messageText = messageText.replace(url, expandedUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def shortenLinksRule(message, data):
  global shortLinkUrls
  
  messageText = message.message
  token = data

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)

  for url in urls:
    newUrl = shortenUrl(url, token)

    messageText = messageText.replace(url, newUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def changeParamsAndShortenLinkRule(message, data):
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

    messageText = messageText.replace(url, expandedUrlWithNewParams)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}

def makeRonokoLink(url, ronokoId):
  UrlEncodedId = urllib.quote_plus(ronokoId)
  UrlEncodedUrl = urllib.quote_plus(url)
  
  rnkoUrl = 'https://roanokevalleyredcross.org/blog.html?'
  rnkoUrl += f'?id={UrlEncodedId}'
  rnkoUrl += f'&url={UrlEncodedUrl}'
  
  return rnkoUrl

def ronkovalleyLinkRule(message, data):
  global shortLinkUrls
  
  messageText = message.message

  ruleData = data.split('|')

  paramsAndValues = ruleData[0]
  token = ruleData[1]
  ronokoId = ruleData[2]

  extractor = URLExtract()

  urls = extractor.find_urls(messageText)


  for url in urls:
    expandedUrl = url
    
    for shortener in shortLinkUrls:
      if shortener in url.lower():
        expandedUrl = expandUrl(url)

    paramGroups = paramsAndValues.split(';')
    expandedUrlWithNewParams = addParamToLink(expandedUrl, paramGroups)

    newUrl = expandedUrlWithNewParams

    if expandedUrlWithNewParams.startswith('https://amazon') or expandedUrlWithNewParams.startswith('http://amazon') or expandedUrlWithNewParams.startswith('amazon'):
      newUrl = shortenUrl(expandedUrlWithNewParams, token)
    else:
      ronokoLink = makeRonokoLink(expandedUrlWithNewParams, ronokoId)
      newUrl = shortenUrl(ronokoLink, token)

    messageText = messageText.replace(url, newUrl)
  
  message.message = messageText
  
  return {'message': message, 'hasPassed': True, 'dontSend': False}
