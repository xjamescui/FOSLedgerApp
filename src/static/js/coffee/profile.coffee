do ->
  'use strict'

  # membership profile
  accountIdLabel                = $('#profile-info-container #account-value')
  creditLabel                   = $('#profile-info-container #credits-value')
  pointsLabel                   = $('#profile-info-container #points-value')

  # member enrollment form
  enrollForm                    = document.forms['enroll-form']
  enrollFormErrorPrompt         = $(enrollForm).find('#enroll-form-error')
  enrollEmailField              = $(enrollForm.email)
  enrollSubmitButton            = $('#enroll-form-container #new-member-add-button')

  # credit conversion form
  convertCreditsForm            = document.forms['convert-form']
  convertCreditsEmailField      = $(convertCreditsForm.email)
  convertCreditsValueField      = $(convertCreditsForm.credits)
  convertCreditsPtsEstimate     = $(convertCreditsForm).find('#pts-estimate')
  convertCreditsFormErrorPrompt = $(convertCreditsForm).find('#convert-form-error')
  convertCreditsButton          = $('#convert-form-container #convert-submit-button')
  convertCreditsEstimateButton  = $('#convert-form-container #pts-estimate-button')

  # Form: Add Purchase
  newPurchaseForm               = document.forms['new-purchase-form']
  newPurchaseEmailField         = $(newPurchaseForm.email)
  priceField                    = $(newPurchaseForm.purchase_price)
  descriptionField              = $(newPurchaseForm.purchase_description)
  dayField                      = $(newPurchaseForm.purchase_day)
  monthField                    = $(newPurchaseForm.purchase_month)
  yearField                     = $(newPurchaseForm.purchase_year)
  newPurchaseSubmitButton       = $('#new-purchase-add-button')
  newPurchaseFormErrorPrompt    = $('#new-purchase-form-error')

  # lists to render
  purchasesList                 = $('ul#purchases-list')
  membersList                   = $('ul#members-list')


  secretKey = 123 # hardcode this on the client side for now

  ##################
  # Utility functions
  ##################

  numToCurrency = (num)->
    '$' + num.toFixed(2)

  formatDateString = (dateStr)->
    dateStr.substr(0, 10) # this gets the yyyy-mm-dd part

  formatPointsString = (pts)->
    pts + ' pts'

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
    dayField.val(now.getDate())
    monthField.val(now.getMonth() + 1)
    yearField.val(now.getUTCFullYear())
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

  ##################
  # Utils needed for BONUS questions
  ##################

  # general function to create a sig hash
  createSig = (secretKey, params)->
    # prepend secret key
    sig = secretKey.toString()

    # sort params and append
    if params != {}
      Object.keys(params).sort().forEach (k)->
        sig = sig + k + params[k]

    # compute md5 hash
    calcMD5(sig)

  # signs the params with sig
  # called for every ajax method
  signedParams = (params) ->
    params = if params == undefined then {} else params
    params['sig'] = createSig(secretKey, params)
    return params


  ##################
  # User overview
  ##################

  refreshUserOverview = ->
    $.get '/api/current_user_details', signedParams(), (result) ->
        accountIdLabel.text result['user']['account_id']
        pointsLabel.text result['points']
        creditLabel.text result['credits']
        return
    return

  initUserOverview = ->
    initConvertCreditsForm()
    refreshUserOverview()

  ##################
  # Enrollment
  ##################

  refreshMembersList = ()->
    $.get '/api/current_user_details/members', signedParams(), (result)->
        members = result['members']
        membersList.empty()
        members.map (m)->
          addRowMembersList(m['email'], m['points'], m['credits'], m['eligibility'])
        return
    return

  getEligibilityStatusLabel = (eligible)->
    if eligible then 'Eligible' else 'Not Eligible'

  addRowMembersList = (email, points, credits, eligibility)->
    membersList.prepend $('<li>' +
        '<div class="item-description">' +
        '<span class="item-title">' + email + '</span>' +
        '<span class="item-subtitle">' + getEligibilityStatusLabel(eligibility) + '</span>' +
        '</div>' +
        '<div class="item-label1">' + credits + '</div>' +
        '<div class="item-label2">' + points + '</div>' +
        '</li>')
    return

  validateEnrollmentInfo = ()->
    email = enrollEmailField.val()
    if !email or email == ''
      updateErrorMsg('Please enter a valid email', enrollFormErrorPrompt)
      return false
    true

  submitEnrollment = ->
    if validateEnrollmentInfo()
      params =
        email: enrollEmailField.val()
      $.post '/api/member', signedParams(params), (result)->
          refreshMembersList()
          return
    return

  initEnrollmentForm = ->
    enrollFormErrorPrompt.hide()
    enrollEmailField.click ->
      updateErrorMsg('', enrollFormErrorPrompt)

    enrollSubmitButton.bind('click', submitEnrollment)
    refreshMembersList()
    return


  ##################
  # Credit Conversion
  ##################

  validateCreditConversionInfo = (ignoreEmail)->
    email   = convertCreditsEmailField.val()
    credits = convertCreditsValueField.val()

    if !ignoreEmail and (!email or email == '')
      updateErrorMsg('Please enter an email', convertCreditsFormErrorPrompt)
      return false
    if !credits or isNaN(credits) or credits < 0
      updateErrorMsg('Invalid value', convertCreditsFormErrorPrompt)
      return false
    if credits % 1 != 0
      # not an integer/whole number
      updateErrorMsg('You can only convert whole numbers', convertCreditsFormErrorPrompt)
      return false
    true


  updatePtsEstimate = (pts)->
    pts = if isNaN(pts) or pts < 0 then 0 else pts
    convertCreditsPtsEstimate.text(' = ' + formatPointsString(pts))
    return

  getPointsEstimate = ->
    if validateCreditConversionInfo(true)
      $.get '/api/credit_conversion', signedParams({credits_quote: convertCreditsValueField.val()}), (result)->
          updatePtsEstimate(result['points'])
          convertCreditsPtsEstimate.show()
          return
    return


  createNewCreditConversion = ->
    if validateCreditConversionInfo()
      params =
        new_credits: convertCreditsValueField.val()
        email: convertCreditsEmailField.val()

      $.ajax(
        url: '/api/credit_conversion'
        type: 'PUT'
        data: signedParams(params)
        success: (result)->
          refreshUserOverview()
          refreshMembersList()
          return
        error: (err)->
          updateErrorMsg(JSON.parse(err.responseText).message, convertCreditsFormErrorPrompt)
          return
      )
    return

  # Initializes the convert points form when user is eligible
  initConvertCreditsForm = ->
    convertCreditsFormErrorPrompt.hide()
    convertCreditsPtsEstimate.hide()

    $(convertCreditsForm).find('input').click ->
      # toggle error msg when textfield in focus
      updateErrorMsg('', convertCreditsFormErrorPrompt)
      convertCreditsPtsEstimate.hide()

    convertCreditsEstimateButton.bind('click', getPointsEstimate)
    convertCreditsButton.bind('click', createNewCreditConversion)
    return


  ##################
  # New Purchase
  ##################


  refreshPurchasesList = ->
    purchasesList.empty()

    $.get '/api/current_user_details/purchases', signedParams(), (result)->
      purchases = result['purchases']
      purchases.map (p)->
        purchasesList.prepend $('<li>' +
            '<div class="item-description">' +
            '<span class="item-title">' + p['title'] + '</span>' +
            '<span class="item-subtitle email">' + p['email'] + '</span>' +
            '<span class="item-subtitle">' + formatDateString(p['date']) + '</span>' +
            '</div>' +
            '<div class="item-label1">' + numToCurrency(p['price']) + '</div>' +
            '<div class="item-label2">' + p['points'] + '</div>' +
            '</li>')
        return
    return


  validateNewPurchaseInfo = ->
    description = descriptionField.val()
    price       = priceField.val()
    day         = dayField.val()
    month       = monthField.val()
    year        = yearField.val()

    if !description or description == ''
      updateErrorMsg('Please write a description about the purchase', newPurchaseFormErrorPrompt)
      return false
    if !price or isNaN(price) or price < 0
      updateErrorMsg('Please enter a valid price', newPurchaseFormErrorPrompt)
      return false
    if !isValidPurchaseDate(day, month, year)
      updateErrorMsg('Invalid date', newPurchaseFormErrorPrompt)
      return false
    true


  createNewPurchase = ->
    if validateNewPurchaseInfo()
      params =
        title : descriptionField.val()
        price : priceField.val().toString()
        day   : dayField.val()
        month : monthField.val()
        year  : yearField.val()
        email : newPurchaseEmailField.val()

      # POST to backend
      $.ajax(
        url:'/api/purchase'
        type: 'POST'
        data: signedParams(params)
        success: (result) ->
          refreshPurchasesList()
          refreshMembersList()
          refreshUserOverview()
          return
        error: (err) ->
          updateErrorMsg(JSON.parse(err.responseText).message, newPurchaseFormErrorPrompt)
          return
      )
    return


  initNewPurchaseForm = ->
    newPurchaseFormErrorPrompt.hide()
    $(newPurchaseForm).children('input').click ->
      updateErrorMsg('', newPurchaseFormErrorPrompt)

    newPurchaseSubmitButton.bind('click', createNewPurchase)
    setDefaultPurchaseDate()
    refreshPurchasesList()
    return


  ##################
  # main
  ##################

  main = ->
    initUserOverview()
    initEnrollmentForm()
    initNewPurchaseForm()
    return

  # run
  main()