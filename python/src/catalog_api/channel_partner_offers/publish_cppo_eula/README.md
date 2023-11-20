## How to use this sample code

1. AWS MP account is a channel partner reseller account
2. You should have an active resale authorization with resale authorization ID
    to proceed with CPPO creation
3. Make sure the information inside the resale authorization matches the offer(s) you intend to create.
    i.e. product type, one time resale authorization, multi use resale authorization with/without expiry dates, etc
4. Make sure to modify the following parameters based on the offer requiremnts
    in the beginning of the script.

    # resale authorization id
        resaleAuthorizationId = 'resaleauthz-1111111111111'
    # legal term url. Need to have access to this legal term document from AWS MP account
        legalTermUrl = 'https://aws-mp-standard-contracts.s3.amazonaws.com/Standard-Contact-for-AWS-Marketplace-2022-07-14.pdf'
    # buyer account id
        buyerAccount = '111111111111'
    # availability end date
        availabilityEndDate = '2023-05-31'
    # agreement duration
        agreementDuration = 'P450D'
