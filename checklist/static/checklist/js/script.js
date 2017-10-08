function regexMatch() {
    var regex_str = $("#regex_entry").val();
    var re = RegExp(regex_str);
    var match_str = $("#match_area").val();
    var matches = re.searchf(match_str);
    
}