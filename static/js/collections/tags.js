var app = app || {};
var TagCollection = Backbone.Collection.extend({
    model: app.Tag,
    url: '/api/v1/tags/'
});
app.Tags = new TagCollection();