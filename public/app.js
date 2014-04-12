angular.module("myApp", [])
.value("loadingMessages", [
    "Heating up Mom's spaghetti",
    "Brushing dirt off shoulder",
    "Dropping it like it's hot",
    "Getting low"
])
.controller("Main", ["$scope", "$http", "loadingMessages", function($scope, $http, loadingMessages) {

  $scope.start = $scope.end = "";
  $scope.results = [];
  $scope.isLoading = false;
  $scope.loadingMessage = "Loading"

  var searchCount = 0;

  $scope.search = function() {
      $scope.results = [];

      $scope.isLoading = true;
      $scope.loadingMessage = loadingMessages[searchCount++ % loadingMessages.length];

      $http.get('/api/path?start='+$scope.start+"&end="+$scope.end).success(function(data){
        $scope.results = data;
        data.forEach(function(p){  ytSearch(p, p.song, [p.start, p.end]) });
        setTimeout(function(){ 
          $scope.$apply(function(){ $scope.isLoading = false;});
        }, 1500);
      });
  }

  function ytSearch(p, song, artists) {
    var query = artists.slice()
    query.unshift(song);
    query = query.join(" ");
    var url = "https://gdata.youtube.com/feeds/api/videos?alt=json&q="+encodeURIComponent(query);
    $http.get(url).success(function(data){
      var idParts = data.feed.entry[0].id["$t"].split("/");
      p.ytId = idParts[idParts.length -1];
    });
  }

}])
.directive('youtube', function() {
  return {
    restrict: 'E',
    template: '<div style="text-align:center"><iframe width="420" height="315" frameborder="0" allowfullscreen></iframe></div>',
    link: function(scope, element, attrs) {
      console.log(attrs, attrs.ytId);
      angular.element(element).find("iframe").attr("src", "http://www.youtube.com/embed/"+attrs.ytId);
    }
  };
});

