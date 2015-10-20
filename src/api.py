from flask import jsonify
from flask_restful import Resource, Api, reqparse
from flask_login import current_user
from models import Purchase, Membership
import datetime

api = Api()

'''
API endpoints/Resources
'''


class BaseResource(Resource):
    def __init__(self):
        # parser to parse request params
        self.parser = reqparse.RequestParser()


class CurrentUserDetailsResource(Resource):
    """
    Provides profile info about the logged in user
    """

    def get(self):
        if not current_user:
            return None

        purchases_by_date_most_recent = sorted(current_user.membership.purchases, key=lambda x: x.date)

        return jsonify({
            'user': current_user.serialize(),
            'credits': current_user.membership.credits,
            'points': current_user.membership.points,
            'eligible': current_user.membership.is_reward_eligible(),
            'max_eligible': current_user.membership.max_reward_eligible(),
            'purchases': [p.serialize() for p in purchases_by_date_most_recent]
        })


class PurchaseResource(BaseResource):
    """
    API based on the Purchase Model
    """

    def post(self):
        """
        Creating a new Purchase object for the logged in user
        """
        self.parser.add_argument('title', type=str, required=True)
        self.parser.add_argument('price', type=float, required=True)
        self.parser.add_argument('day', type=int, required=True)
        self.parser.add_argument('month', type=int, required=True)
        self.parser.add_argument('year', type=int, required=True)
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
            'eligible': current_user.membership.is_reward_eligible(),
            'max_eligible': current_user.membership.max_reward_eligible(),
            'purchases': [p.serialize() for p in current_user.membership.purchases]
        })
        pass


class CreditConversionResource(BaseResource):
    """
    Handles all requests to convert points into credits for the logged in user
    """

    def get(self):
        """
        Given a credit value, give the # points needed to get that credit
        """
        self.parser.add_argument('credits_quote', type=int, required=True)
        args = self.parser.parse_args()
        credits = args.get('credits_quote')
        return jsonify({
            'points': current_user.membership.points_needed_for(credits)
        })

    def put(self):
        """
        Update membership by converting points into credits, if appropriate
        """
        self.parser.add_argument('new_credits', type=int, required=True)
        args = self.parser.parse_args()
        credits_to_add = args.get('new_credits', 0)

        converted = current_user.membership.convert_points_for(credits_to_add)

        results = {
            'credits': current_user.membership.credits,
            'points': current_user.membership.points,
            'eligible': current_user.membership.is_reward_eligible(),
            'max_eligible': current_user.membership.max_reward_eligible()
        }

        if not converted:
            results['backend_err_msg'] = 'Conversion failed. Insufficient Points or Ineligible.'

        return jsonify(results)


# Register all created API resources
api.add_resource(PurchaseResource, '/api/purchase')
api.add_resource(CurrentUserDetailsResource, '/api/current_user_details')
api.add_resource(CreditConversionResource, '/api/credit_conversion')
