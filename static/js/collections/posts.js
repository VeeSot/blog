var app = app || {};
var PostCollection = Backbone.Collection.extend({
    model: app.Post,
    url: '/api/v1/posts/'
});
app.Posts = new PostCollection();