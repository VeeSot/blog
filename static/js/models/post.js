var app = app || {};
app.Post = Backbone.Model.extend({
    defaults: {
        title: '',
        created_at: '',
        slug: '',
        body: ''
    }
});