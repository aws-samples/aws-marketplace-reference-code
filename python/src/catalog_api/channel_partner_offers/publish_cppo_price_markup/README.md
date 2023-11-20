## How to use this sample code

1. AWS MP account is a channel partner reseller account
2. You should have an active resale authorization with resale authorization ID
    to proceed with CPPO creation
3. Make sure the information inside the resale authorization matches the offer(s) you intend to create.
    i.e. product type, one time resell authorization, multi use resale authorization with/without expiry dates, etc
4. Make sure to modify the following parameters based on the offer requiremnts in the beginning of the script.

    # number of offers you want to create with this resale authorization. Default is set to 1.
    # number of offers you want to create with this resale authorization. Default is set to 1.
    # For one time resale authorization, this needs to be set at 1.
    # To create multiple CPPOs with one multi use Resale Authorization ID,
    # modify this value to the number of CPPOs you want to create.
        numbOfCPPOs = 1
    # resale authorization id
        resaleAuthorizationId = 'resaleauthz-1111111111111'
    # price markup percentage
        priceMarkupPer = '5.0'
    # buyer account id
        buyerAccount = '111111111111'
    # availability end date
        availabilityEndDate = '2023-05-31'
    # agreement duration
        agreementDuration = 'P450D'
