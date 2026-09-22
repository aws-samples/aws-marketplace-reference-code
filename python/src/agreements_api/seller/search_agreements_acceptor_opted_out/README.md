## How to use this sample code

1. Valid AWS Marketplace proposer account. This filter is supported only when PartyType is Proposer.
2. Change the reason code you are searching for based on your need. (PROPOSER_RENEW_OPTED_OUT, ACCEPTOR_RENEW_OPTED_OUT, NO_RENEWAL_TERM, or RENEWAL_LIMIT_EXHAUSTED)
    # change to another reason code if a different non-renewal reason is desired
    endTimeBehaviorReasonCodeFilterValue = 'ACCEPTOR_RENEW_OPTED_OUT'
3. You can choose the number of max results returned per page in the beginning of the script:
    MAX_PAGE_RESULTS = 10
4. Leave PartyType set to "Proposer". "Acceptor" fails with a ValidationException (UNSUPPORTED_FILTERS) for this filter.
