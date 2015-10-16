from flask_assets import Bundle, Environment

"""
    prepares and compress the assets: js, css files that load on the front-end
"""
assets = Environment()

bundles = {

    'layout_css': Bundle(
        Bundle('css/sass/layout.sass', filters='sass'),
        output='css/layout.css',
        filters='cssmin'
    ),

    'portal_css': Bundle(
        Bundle('css/sass/portal.sass', filters='sass'),
        output='css/portal.css',
        filters='cssmin'
    ),

    # 'profile_js': Bundle(),
    # 'profile_css': Bundle()
}

assets.register(bundles)
