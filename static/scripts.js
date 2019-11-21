$('document').ready( function(){

    // n closest concepts menu
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
            $('#wiktionary-nav').removeClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#dbpedia-nav').removeClass('active');
            $('#alod-nav').addClass('active');
    });

    $('#dbpedia-nav').click(
        function(){
            $('#wiktionary-nav').removeClass('active');
            $('#wordnet-nav').removeClass('active');
            $('#babelnet-nav').removeClass('active');
            $('#alod-nav').removeClass('active');
            $('#dbpedia-nav').addClass('active');
    });


    // similarity menu
    $('#wiktionary-sim-nav').click(
        function(){
            $('#wiktionary-sim-nav').addClass('active');
            $('#wordnet-sim-nav').removeClass('active');
            $('#babelnet-sim-nav').removeClass('active');
            $('#alod-sim-nav').removeClass('active');
            $('#dbpedia-sim-nav').removeClass('active');
    });

    $('#babelnet-sim-nav').click(
        function(){
            $('#wiktionary-sim-nav').removeClass('active');
            $('#wordnet-sim-nav').removeClass('active');
            $('#babelnet-sim-nav').addClass('active');
            $('#alod-sim-nav').removeClass('active');
            $('#dbpedia-sim-nav').removeClass('active');
    });

    $('#wordnet-sim-nav').click(
        function(){
            $('#wiktionary-sim-nav').removeClass('active');
            $('#wordnet-sim-nav').addClass('active');
            $('#babelnet-sim-nav').removeClass('active');
            $('#alod-sim-nav').removeClass('active');
            $('#dbpedia-sim-nav').removeClass('active');
    });

    $('#alod-sim-nav').click(
        function(){
            $('#wiktionary-sim-nav').removeClass('active');
            $('#wordnet-sim-nav').removeClass('active');
            $('#babelnet-sim-nav').removeClass('active');
            $('#dbpedia-sim-nav').removeClass('active');
            $('#alod-sim-nav').addClass('active');
    });

    $('#dbpedia-sim-nav').click(
        function(){
            $('#alod-sim-nav').removeClass('active');
            $('#wordnet-sim-nav').removeClass('active');
            $('#babelnet-sim-nav').removeClass('active');
            $('#wiktionary-sim-nav').removeClass('active');
            $('#dbpedia-sim-nav').addClass('active');
    });

    // closest vector menu
    $('#similarity-button').click(
        async function(){
            $("#similarity-result").html('<center><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></center>')
            console.log("Closest Search Button clicked.")
            concept_1 = $("#concept1sim").val()
            concept_2 = $("#concept2sim").val()
            if(concept_1 == '' || concept_2 == '') {
                $("#similarity-result").html('<center><p>Please specify both concept labels.</p></center>')
                return
            }

            console.log("Concept 1 Term: " + concept_1)
            console.log("Concept 2 Term: " + concept_2)

            service = ''
            if($("#alod-sim-nav").hasClass('active')) {
                service = 'alod'
            } else if ( $("#wordnet-sim-nav").hasClass('active')) {
                service = 'wordnet'
            } else if ( $("#babelnet-sim-nav").hasClass('active')) {
                service = 'babelnet'
            } else if ( $("#wiktionary-sim-nav").hasClass('active')) {
                service = 'wiktionary'
            } else if ( $("#dbpedia-sim-nav").hasClass('active')) {
                service = 'dbpedia'
            }

            if(service == '') {
                console.log("ERROR - query service could not be determined.")
                return
            }

            const request_uri = '/rest/get-similarity/' + service + '/' + encodeURI(concept_1) + "/" + concept_2
            console.log("Request GET: " + request_uri)
            const response = await fetch(request_uri)
            const result = await response.json();
            stringify_response = JSON.stringify(result)
            console.log("Response:" +  stringify_response)
            $("#similarity-result").html('<center><p>' + result.result + '</p></center>')


        }
    );


    $('#query-search-button').click(
        async function(){
            $("#query-result").html('<center><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></center>')
            console.log("Closest Search Button clicked.")
            search_term = $('#search_field').val()
            if(search_term == ''){
                $("#query-result").html('<center><p>Please specify a label to search for.</p></center>')
                return
            }
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