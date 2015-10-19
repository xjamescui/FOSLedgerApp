from flask import jsonify
from flask_restful import Resource, Api, reqparse
from flask_login import current_user
from models import Purchase, Membership
import datetime

api = Api()

'''
API endpoints/Resources
'''


class CurrentUserDetailsResource(Resource):
    def get(self):
        if not current_user:
            return None

        return jsonify({
            'user': current_user.serialize(),
            'credits': current_user.membership.credits,
            'points': current_user.membership.points,
            'purchases': [p.serialize() for p in current_user.membership.purchases]
        })


class PurchaseResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True)
        self.parser.add_argument('price', type=float, required=True)
        self.parser.add_argument('day', type=int, required=True)
        self.parser.add_argument('month', type=int, required=True)
        self.parser.add_argument('year', type=int, required=True)

    def post(self):
        args = self.parser.parse_args()
        title, price = args.get('title'), args.get('price')
        month, day, year = args.get('month'), args.get('day'), args.get('year')

        new_purchase = Purchase.create(membership_id=current_user.membership.id,
                                       title=title,
                                       price=price,
                                       date=datetime.datetime(year, month, day))
        if new_purchase:
            current_user.membership.update(
                points=current_user.membership.points + Membership.price_to_points(new_purchase.points))

        return jsonify({
            'credits': current_user.membership.credits,
            'points': current_user.membership.points,
            'purchases': [p.serialize() for p in current_user.membership.purchases]
        })
        pass


api.add_resource(PurchaseResource, '/api/purchase')
api.add_resource(CurrentUserDetailsResource, '/api/current_user_details')
