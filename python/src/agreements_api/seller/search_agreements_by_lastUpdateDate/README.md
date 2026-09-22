## How to use this sample code

1. Valid AWS Marketplace proposer account. This filter is supported only when PartyType is Proposer.
2. Change date search criteria based on your need. (AfterLastUpdateTime or BeforeLastUpdateTime)
    # change to 'BeforeLastUpdateTime' if before last update time is desired
    beforeOrAfterLastUpdatetimeFilterName = 'AfterLastUpdateTime'
3. Date format needs to be in ISO 8601 format.
    i.e. 'YYYY-MM-DDThh:mm:ssZ'
    cutoffDate = '2024-11-18T00:00:00Z'
4. You can choose the number of max results returned per page in the beginning of the script:
    MAX_PAGE_RESULTS = 10
5. Leave PartyType set to "Proposer". "Acceptor" fails with a ValidationException (UNSUPPORTED_FILTERS) for this filter.
