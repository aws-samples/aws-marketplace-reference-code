## How to use this sample code

1. Valid AWS MP seller's account
2. Change date search criteria based on your need. (AfterEndtime or BeforeEndTime)
    # change to 'AfterEndTime' if after endtime is desired
    beforeOrAfterEndtimeFilterName = 'BeforeEndTime'
3. Date format nees to be in ISO 8601 format.
    i.e. 'YYYY-MM-DDThh:mm:ssZ'
    cutoffDate = '2300-03-08T00:00:00Z'
3. You can choose the number of max results returned per page in the beginning of the script:
    MAX_PAGE_RESULTS = 10
4. Search by account id only works for PartyType = "Proposer"