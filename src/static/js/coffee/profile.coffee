do ->
  'use strict'

  # membership profile
  emailLabel = $('#top-nav-bar #email-label')
  accountIdLabel = $('#profile-info-container #account-value')
  creditLabel = $('#profile-info-container #credits-value')
  pointsLabel = $('#profile-info-container #points-value')

  # list of purchases/activities
  purchasesList = $('ul#purchases-list')

  # Form: Add Purchase
  allFields = $('#new-purchase-form input')
  priceTextField = $('#new-purchase-price')
  titleTextField = $('#new-purchase-title')
  dayTextField = $('#new-purchase-day')
  monthTextField = $('#new-purchase-month')
  yearTextField = $('#new-purchase-year')
  newPurchaseAddButton = $('#new-purchase-add-button')
  formErrorPrompt = $('#form-error')

  # data model
  secret_key = null
  accountId = ''
  email = ''
  points = 0
  credits = 0
  formError = ''

  numToCurrency = (num)->
    '$' + num.toFixed(2)

  formatDateString = (dateStr)->
    dateStr.substr(0, 10) # this gets the yyyy-mm-dd part

  formatPointsString = (pts)->
    pts + ' pts'

  updateAccountId = (id) ->
    accountId = id
    accountIdLabel.text(accountId)
    return

  updateEmail = (newEmail) ->
    email = newEmail
    emailLabel.text(email)
    return

  updateCredits = (newCredits)->
    credits = newCredits
    creditLabel.text(credits)
    return

  updatePoints = (newPoints)->
    points = newPoints
    pointsLabel.text(points)
    return

  updateSecretKey = (newKey) ->
    secret_key = newKey
    return

  updatePurchasesList = (purchases) ->
    purchasesList.empty()

    # re-populate with new data
    purchases.map (p) ->
      purchasesList.prepend($('<li>' +
          '<div class="item-description">' +
          '<span class="item-title">' + p['title'] + '</span>' +
          '<span class="item-date">' + formatDateString(p['date']) + '</span>' +
          '</div>' +
          '<div class="item-price">' + numToCurrency(p['price']) + '</div>' +
          '<div class="item-points">' + formatPointsString(p['points']) + '</div>' +
          '</li>'))
    return

  setDefaultPurchaseDate = ()->
    now = new Date()
    dayTextField.val now.getDate()
    monthTextField.val now.getMonth() + 1
    yearTextField.val now.getUTCFullYear()
    return

  isValidPurchaseDate = (day, month, year) ->
    return false if (isNaN(day) or isNaN(month) or isNaN(year))
    today = new Date()
    date = new Date(year, month - 1, day)
    # cannot buy something in the "future" i.e. later than present
    return false if date.getTime() > today.getTime()
    # date is just wrong in general (e.g. February 30 does not exist)
    return false if !(date.getFullYear() == parseInt(year) and date.getMonth() + 1 == parseInt(month) and date.getDate() == parseInt(day))
    true

  validateNewPurchaseInfo = ()->
    if !titleTextField.val() or titleTextField.val() == ''
      formError = 'Please write a description about the purchase'
      return false
    if !priceTextField.val() or isNaN(priceTextField.val()) or priceTextField.val() < 0
      formError = 'Please enter a price'
      return false
    if !isValidPurchaseDate(dayTextField.val(), monthTextField.val(), yearTextField.val())
      formError = 'Invalid date'
      return false
    true

  updateErrorMsg = (msg)->
    if msg and msg != ''
      formErrorPrompt.text(msg)
      formErrorPrompt.show()
    else
      formErrorPrompt.hide()

  createNewPurchase = (list) ->
    if !validateNewPurchaseInfo()
      updateErrorMsg(formError)
    else
      params =
        title: titleTextField.val()
        price: priceTextField.val()
        day: dayTextField.val()
        month: monthTextField.val()
        year: yearTextField.val()

      # POST to backend
      $.ajax(
        url: '/api/purchase',
        type: 'POST',
        data: params
        success: (result) ->
          # add new data to UI
          updateCredits(result['credits'])
          updatePoints(result['points'])
          updatePurchasesList(result['purchases'])
          return
        error: (err)->
          console.log err
          return
      )
    return

  initNewPurchaseForm = ()->
    formErrorPrompt.hide()
    allFields.click () ->
      updateErrorMsg('')
    newPurchaseAddButton.bind('click', createNewPurchase.bind(this, purchasesList))
    setDefaultPurchaseDate()
    return

  init = ->
    initNewPurchaseForm()

    # GET secret key and other user info
    $.ajax(
      url: '/api/current_user_details'
      type: 'GET'
      success: (result) ->
        updateEmail(result['user']['email'])
        updateAccountId(result['user']['account_id'])
        updateCredits(result['credits'])
        updatePoints(result['points'])
        updateSecretKey(result['secret_key'])
        updatePurchasesList(result['purchases'])
        return
      error: (err) ->
        console.log err
        return
    )
    return

  # run
  init()