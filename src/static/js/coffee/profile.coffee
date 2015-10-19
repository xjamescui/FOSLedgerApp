do ->
  'use strict'

  # membership profile
  emailLabel = $('#profile-info-container #email-label')
  creditLabel = $('#profile-info-container #credits-label')
  pointsLabel = $('#profile-info-container #points-label')

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
  email = null
  points = 0
  credits = 0
  formError = ''

  numToCurrency = (num)->
    '$' + num.toFixed(2)

  formatDateString = (dateStr)->
    dateStr.substr(0, 10) # this gets the yyyy-mm-dd part

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
          '<span class="item-title">' + p['title'] + '</span>' +
          '<span class="item-date">' + formatDateString(p['date']) + '</span>' +
          '<span class="item-price">' + numToCurrency(p['price']) + '</span>' +
          '<span class="item-points">' + p['points'] + '</span>' +
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
    date  = new Date(year, month - 1, day)

    # cannot buy something in the "future" i.e. later than present
    return false if date.getTime() > today.getTime()
    # date is just wrong in general (e.g. February 30 does not exist)
    return false if !(date.getFullYear() == parseInt(year) and date.getMonth() + 1 == parseInt(month) and date.getDate() == parseInt(day))

    true

  validateNewPurchaseInfo = ()->
    if !titleTextField.val() or titleTextField.val() == ''
      formError = 'Must specify a title'
      return false
    if !priceTextField.val() or isNaN(priceTextField.val()) or priceTextField.val() < 0
      formError = 'Please enter a number for price'
      return false
    if !isValidPurchaseDate(dayTextField.val(), monthTextField.val(), yearTextField.val())
      formError = 'Invalid date'
      return false
    true

  updateErrorMsg = (msg)->
    formErrorPrompt.text(msg)
    return

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