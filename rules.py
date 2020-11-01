def filterMessage(message, rules):
  # The rule will be like: N_N_TEXT
  # Where "N" is a number 1-9
  # First N is group of rule, second in rule option
  # And the "TEXT" is a string built in a way reffering to "N"
  newMessage = message
  hasPassed = True

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

  return { 'message': newMessage, 'hasPassed': hasPassed }

# fuctions
def wordWhiteList(message, words):
  wordsArr = words.split(':')

  timesWordRepeated = 0

  for word in wordsArr:
    if word in message.message:
      timesWordRepeated += 1

  if timesWordRepeated:
    return {'message': message, 'hasPassed': True}
  else:
    return {'message': message, 'hasPassed': False}