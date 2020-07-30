GET_ALL_CARDS = """{
    repository(name: \"xdev\", owner: \"NCAR\") {
        projects(first: 8, after: \"Y3Vyc29yOnYyOpHOACHFqQ==\") {
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
