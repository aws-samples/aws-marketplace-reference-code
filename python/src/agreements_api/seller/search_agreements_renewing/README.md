## How to use this sample code

1. Valid AWS Marketplace proposer account. This filter is supported only when PartyType is Proposer.
2. Change the end time behavior you are searching for based on your need. (RENEW, REPLACE, or EXPIRE)
    # change to 'REPLACE' or 'EXPIRE' to find the agreements that will not renew
    endTimeBehaviorTypeFilterValue = 'RENEW'
3. You can choose the number of max results returned per page in the beginning of the script:
    MAX_PAGE_RESULTS = 10
4. Leave PartyType set to "Proposer". "Acceptor" fails with a ValidationException (UNSUPPORTED_FILTERS) for this filter.
