## How to use this sample code

1. Valid AWS MP seller's account
2. You can what searching criteria to search with (OfferId/resourceIdentifier/AccepterId):
    # To search by offer id: OfferId;
    # by product id: resourceIdentifier;
    # by customer AWS account id: AcceptorId
    # by product type: resourceType
    idType = "AcceptorId"
    # replace id value as needed
    idValue = '111111111111'
3. You can choose the number of max results returned per page in the beginning of the script:
    MAX_PAGE_RESULTS = 10
4. Search by account id only works for PartyType = "Proposer"