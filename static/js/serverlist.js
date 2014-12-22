if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
    return this.indexOf(str) == 0;
  };
}
$.ajax({
    type: 'GET',
    url: 'http://www.corsproxy.com/www.classicube.net/api/serverlist/',
    dataType: 'json',
    cache: false,
    success: function(result) {
      var new_result = [];
      for (var key in result) {
        if (result[key]['software'].startsWith('LegendCraft')) {
          new_result.push(result[key]);
        }
      };
      var source = " \
        <table class='table' id='table-main'> \
          <thead> \
            <tr> \
              <th>Server name</th> \
              <th>Server link</th> \
              <th>Players</th> \
            </tr> \
          </thead> \
          <tbody> \
            {{#each data}} \
              <tr> \
                <td>{{this.name}}</td> \
                <td><a href='http://classicube.net/server/play/{{this.hash}}/'>PLAY HERE</a></td> \
                <td>{{this.players}}/{{this.maxplayers}}</td> \
              </tr> \
            {{/each}} \
          </tbody> \
        </table> \
      ";
      var template = Handlebars.compile(source);
      $('#table').html(template({data: new_result}));
      $("#table-main").tablesorter({
          // sort on the first column and third column, order asc
          sortList: [[2,1],[0,1]]
      });
    },
});
