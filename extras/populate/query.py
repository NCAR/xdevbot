GET_ALL_CARDS = """{
    repository(name: \"xdev\", owner: \"NCAR\") {
        projects(first: 10) {
            nodes {
                url
                columns(first: 7) {
                    nodes {
                        databaseId
                        name
                        cards(first: 100) {
                            nodes {
                                databaseId
                                note
                                content {
                                  ... on Issue {
                                    databaseId
                                    state: state
                                    type: __typename
                                  }
                                  ... on PullRequest {
                                    databaseId
                                    state: state
                                    type: __typename
                                  }
                                }
                                creator {
                                    login
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}"""
