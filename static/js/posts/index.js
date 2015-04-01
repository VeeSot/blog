var Post = Backbone.Model.extend({
    defaults: {
        title: '',
        slug: '',
        img: '',
        created_at: ''
    }
});
var PostCollection = Backbone.Collection.extend({
    model: Post,
    url: '/api/v1/posts/'
});
var posts = new PostCollection();
posts.fetch();
console.log(posts);
