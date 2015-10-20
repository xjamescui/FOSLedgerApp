do ->
  'use strict'

  # membership profile
  emailLabel       = $('#top-nav-bar #email-label')
  accountIdLabel   = $('#profile-info-container #account-value')
  creditLabel      = $('#profile-info-container #credits-value')
  pointsLabel      = $('#profile-info-container #points-value')
  eligibilityLabel = $('#profile-info-container #eligibility-value')

  # credit conversion form
  convertCreditsForm            = $('#profile-info-container #convert-form')
  convertCreditsTextField       = convertCreditsForm.find('#points-to-convert')
  convertCreditsPtsEstimate     = convertCreditsForm.find('#pts-estimate')
  convertCreditsFormErrorPrompt = convertCreditsForm.find('#convert-form-error')
  convertCreditsButton          = convertCreditsForm.find('#convert-submit-button')
  convertCreditsEstimateButton  = convertCreditsForm.find('#pts-estimate-button')

  # Form: Add Purchase
  newPurchaseForm            = $('#new-purchase-form')
  priceTextField             = $('#new-purchase-price')
  titleTextField             = $('#new-purchase-title')
  dayTextField               = $('#new-purchase-day')
  monthTextField             = $('#new-purchase-month')
  yearTextField              = $('#new-purchase-year')
  newPurchaseAddButton       = $('#new-purchase-add-button')
  newPurchaseFormErrorPrompt = $('#new-purchase-form-error')

  # list of purchases/activities
  purchasesList = $('ul#purchases-list')

  # data model
  secret_key          = null
  accountId           = ''
  email               = ''
  points              = 0
  credits             = 0
  rewardsEligible     = false
  rewardsMaxEligible  = 0

  numToCurrency = (num)->
    '$' + num.toFixed(2)

  formatDateString = (dateStr)->
    dateStr.substr(0, 10) # this gets the yyyy-mm-dd part

  formatPointsString = (pts)->
    pts + ' pts'

  updateAccountId = (id)->
    accountId = id
    accountIdLabel.text(accountId)
    return

  updateEmail = (newEmail)->
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

  updateSecretKey = (newKey)->
    secret_key = newKey
    return

  getEligibilityStatusLabel = (eligible)->
    if eligible then 'Eligible' else 'Not Eligible'

  updateRewardsEligibility = (eligible, maxAllowed)->
    rewardsEligible    = eligible
    rewardsMaxEligible = maxAllowed

    convertCreditsTextField.val(rewardsMaxEligible)
    eligibilityLabel.text(getEligibilityStatusLabel(eligible))
    convertCreditsForm.toggle(rewardsEligible)
    return

  updatePurchasesList = (purchases)->
    purchasesList.empty()

    # re-populate with new data
    purchases.map (p)->
      purchasesList.prepend($('<li>' +
          '<div class="item-description">' +
          '<span class="item-title">' + p['title'] + '</span>' +
          '<span class="item-date">' + formatDateString(p['date']) + '</span>' +
          '</div>' +
          '<div class="item-price">' + numToCurrency(p['price']) + '</div>' +
          '<div class="item-points">' + formatPointsString(p['points']) + '</div>' +
          '</li>'))
    return

  updatePtsEstimate = (pts)->
    pts = if isNaN(pts) or pts < 0 then 0 else pts
    convertCreditsPtsEstimate.text(' = ' + formatPointsString(pts))

  # Toggle error display in different forms.
  # Just specify the error and the error prompt element to display it in
  updateErrorMsg = (msg, errorContainer)->
    if msg and msg != ''
      errorContainer.text(msg)
      errorContainer.show()
    else
      errorContainer.hide()

  setDefaultPurchaseDate = ->
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

  validateNewPurchaseInfo = ->
    if !titleTextField.val() or titleTextField.val() == ''
      updateErrorMsg('Please write a description about the purchase', newPurchaseFormErrorPrompt)
      return false
    if !priceTextField.val() or isNaN(priceTextField.val()) or priceTextField.val() < 0
      updateErrorMsg('Please enter a valid price', newPurchaseFormErrorPrompt)
      return false
    if !isValidPurchaseDate(dayTextField.val(), monthTextField.val(), yearTextField.val())
      updateErrorMsg('Invalid date', newPurchaseFormErrorPrompt)
      return false
    true


  validateCreditConversionInfo = ->
    inputCredits = convertCreditsTextField.val()
    if !inputCredits or isNaN(inputCredits) or inputCredits < 0
      updateErrorMsg('Invalid value', convertCreditsFormErrorPrompt)
      return false
    if inputCredits % 1 != 0
      # not an integer/whole number
      updateErrorMsg('You can only convert whole numbers', convertCreditsFormErrorPrompt)
      return false
    true


  createNewPurchase = ->
    if validateNewPurchaseInfo()
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
          if result['backend_err_msg']
            updateErrorMsg(result['backend_err_msg'], newPurchaseFormErrorPrompt)
          updatePoints(result['points'])
          updateCredits(result['credits'])
          updateRewardsEligibility(result['eligible'], result['max_eligible'])
          updatePurchasesList(result['purchases'])
          return
        error: (err)->
          updateErrorMsg(err.responseText, newPurchaseFormErrorPrompt)
          return
      )
    return

  createNewCreditConversion = ->
    if validateCreditConversionInfo()
      $.ajax(
        url: '/api/credit_conversion'
        type: 'PUT'
        data: {new_credits: convertCreditsTextField.val()}
        success: (result)->
          if result['backend_err_msg']
            updateErrorMsg(result['backend_err_msg'], convertCreditsFormErrorPrompt)
          updatePoints(result['points'])
          updateCredits(result['credits'])
          updateRewardsEligibility(result['eligible'], result['max_eligible'])
          return
        error: (err)->
          updateErrorMsg(err.responseText, convertCreditsFormErrorPrompt)
          return
      )
    return

  getPointsEstimate = ->
    if validateCreditConversionInfo()
      $.ajax(
        url: '/api/credit_conversion'
        type: 'GET'
        data: {credits_quote: convertCreditsTextField.val()}
        success: (result)->
          updatePtsEstimate(result['points'])
          convertCreditsPtsEstimate.show()
          return
        error: (err)->
          updateErrorMsg(err.responseText, convertCreditsFormErrorPrompt)
          return
      )
    return

  # Initializes the convert points form when user is eligible
  initConvertCreditsForm = ->
    convertCreditsFormErrorPrompt.hide()
    convertCreditsPtsEstimate.hide()

    convertCreditsTextField.click ->
      # toggle error msg when textfield in focus
      updateErrorMsg('', convertCreditsFormErrorPrompt)
      convertCreditsPtsEstimate.hide()

    convertCreditsEstimateButton.bind('click', getPointsEstimate)
    convertCreditsButton.bind('click', createNewCreditConversion)

    if !rewardsEligible
      convertCreditsForm.hide()
    else
      convertCreditsForm.show()
      convertCreditsTextField.val(rewardsMaxEligible) # default to max credits eligible
    return

  initNewPurchaseForm = ->
    newPurchaseFormErrorPrompt.hide()

    # setup error msg toggling
    newPurchaseForm.children('input').click ->
      updateErrorMsg('', newPurchaseFormErrorPrompt)

    newPurchaseAddButton.bind('click', createNewPurchase)
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
        updateRewardsEligibility(result['eligible'], result['max_eligible'])
        initConvertCreditsForm()
        return
      error: (err) ->
        console.log err
        return
    )
    return

  # run
  init()