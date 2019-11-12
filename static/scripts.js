$('document').ready( function(){
    $('#wiktionary-nav').click(
        function(){
            $('#wiktionary-nav').addClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#alod-nav').removeClass('active');
            $('#dbpedia-nav').removeClass('active');
    });

    $('#babelnet-nav').click(
        function(){
            $('#wiktionary-nav').removeClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').addClass('active');
            $('#alod-nav').removeClass('active');
            $('#dbpedia-nav').removeClass('active');
    });

    $('#wordnet-nav').click(
        function(){
            $('#wiktionary-nav').removeClass('active');
            $('#wordnet-nav').addClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#alod-nav').removeClass('active');
            $('#dbpedia-nav').removeClass('active');
    });

    $('#alod-nav').click(
        function(){
            $('#alod-nav').removeClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#alod-nav').addClass('active');
            $('#dbpedia-nav').removeClass('active');
    });

    $('#dbpedia-nav').click(
        function(){
            $('#alod-nav').removeClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#alod-nav').removeClass('active');
            $('#dbpedia-nav').addClass('active');
    });

    $('#query-search-button').click(
        async function(){
            $("#query-result").html('<center><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></center>')
            console.log("Search Button clicked.")
            search_term = $('#search_field').val()
            console.log("Search Term: " + search_term)

            service = ''
            if($("#alod-nav").hasClass('active')) {
                service = 'alod'
            } else if ( $("#wordnet-nav").hasClass('active')) {
                service = 'wordnet'
            } else if ( $("#babelnet-nav").hasClass('active')) {
                service = 'babelnet'
            } else if ( $("#wiktionary-nav").hasClass('active')) {
                service = 'wiktionary'
            } else if ( $("#dbpedia-nav").hasClass('active')) {
                service = 'dbpedia'
            }

            if(service == '') {
                console.log("ERROR - query service could not be determined.")
                return
            }

            const request_uri = '/rest/closest-concepts/' + service + '/10/' + encodeURI(search_term)
            console.log("Request GET: " + request_uri)
            const response = await fetch(request_uri)
            const table = await response.json();
            stringify_response = JSON.stringify(table)
            console.log("Response:" +  stringify_response)

            if(stringify_response == "{}") {
                $("#query-result").html("Term not found.")
            } else {

            table_to_render = '<table id="query-result-table" class="table"><thead><tr><th scope = "col">#</th><th scope = "col">Concept</th><th scope = "col">Similarity Score</th></tr></thead><tbody>'
            for(var i = 0; i < table.result.length; i++){
                table_to_render += '<tr><th scope="row">' + (i+1) + '</th><td>' + table.result[i].concept + '</td>'
                table_to_render += '<td>' + table.result[i].score + '</td></tr>'
            }
            table_to_render += '</tbody></table>'
            $("#query-result").html(table_to_render);
            console.log("Result table rendered.")
            }
        });
});