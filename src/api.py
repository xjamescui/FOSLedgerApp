from flask import jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_login import current_user
from models import Purchase, Member
import datetime
import hashlib

api = Api()

'''
API endpoints/Resources
'''


class BaseResource(Resource):
    def __init__(self):
        # parser to parse request params
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('sig', type=str, required=True)

    def is_sig_valid(self, sig, secret_key, args):
        """
         checks if a given sig from client is valid
        """
        str_to_hash = secret_key
        for key in sorted(args):
            if key == 'sig':
                continue
            str_to_hash = "%s%s%s" % (str_to_hash, key, args[key])
        hash_str = hashlib.md5(str_to_hash).hexdigest()
        return hash_str == sig

    def _abort_if_invalid_sig(self, sig, secret_key, args):
        if not self.is_sig_valid(sig, secret_key, args):
            abort(403, message='invalid request signature')


class CurrentUserDetailsResource(BaseResource):
    """
    Provides profile info about the logged in user
    """

    def get(self):
        args = self.parser.parse_args()
        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        return jsonify({
            'user': current_user.serialize(),
            'sk': current_user.secret_key,
            'credits': current_user.credits,
            'points': current_user.points
        })


class CurrentUserMembersResource(BaseResource):
    def get(self):
        """
        Get all members belonging to current user
        """
        args = self.parser.parse_args()
        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        members = []
        for m in current_user.members:
            tmp = m.serialize()
            tmp.update({'eligibility': m.is_reward_eligible()})
            members.append(tmp)
        return jsonify(members=members)


class CurrentUserPurchasesResource(BaseResource):
    def get(self):
        """
        Get all purchase activities associated with current user
        """
        args = self.parser.parse_args()
        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        purchases = []
        for p in current_user.purchases:
            tmp = p.serialize()
            tmp.update({'email': p.member.email})
            purchases.append(tmp)
        return jsonify(purchases=purchases)


class MemberResource(BaseResource):
    def post(self):
        """
        Creating a new member
        """
        self.parser.add_argument('email', type=str, required=True)
        args = self.parser.parse_args()

        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        email, account_id = args.get('email'), args.get('account_id')

        m = Member.create(email=email, account_id=current_user.account_id)

        return jsonify(success=(m is not None))


class PurchaseResource(BaseResource):
    """
    API based on the Purchase Model
    """

    def post(self):
        """
        Creating a new Purchase object for the logged in user
        """
        self.parser.add_argument('title', type=str, required=True)
        self.parser.add_argument('price', type=str, required=True)
        self.parser.add_argument('day', type=int, required=True)
        self.parser.add_argument('month', type=int, required=True)
        self.parser.add_argument('year', type=int, required=True)
        self.parser.add_argument('email', type=str, required=True)
        args = self.parser.parse_args()

        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        title, price = args.get('title'), float(args.get('price'))
        month, day, year = args.get('month'), args.get('day'), args.get('year')
        email = args.get('email')

        member = Member.query.filter(Member.email == email).first()

        if not member:
            abort(400, message='invalid member')

        p = Purchase.create(member_id=member.id,
                            title=title,
                            price=price,
                            date=datetime.datetime(year, month, day))
        if p:
            member.add_points(Member.price_to_points(p.price))

        return jsonify(success=(p is not None))


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

        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        credits = args.get('credits_quote')
        return jsonify({
            'points': Member.points_needed_for(credits)
        })

    def put(self):
        """
        Update membership by converting points into credits, if appropriate
        """
        self.parser.add_argument('email', type=str, required=True)
        self.parser.add_argument('new_credits', type=int, required=True)
        args = self.parser.parse_args()

        self._abort_if_invalid_sig(args['sig'], current_user.secret_key, args)

        email, credits_to_add = args.get('email'), args.get('new_credits', 0)

        member = Member.query.filter(Member.email == email, Member.account_id == current_user.account_id).first()

        converted = (member.convert_points_to_these_credits(credits_to_add) is not None)

        err = 'Conversion failed. Insufficient Points or Ineligible.' if not converted else False
        return jsonify(success=converted, backend_err_msg=err)


# Register all created API resources
api.add_resource(MemberResource, '/api/member')
api.add_resource(PurchaseResource, '/api/purchase')
api.add_resource(CurrentUserDetailsResource, '/api/current_user_details')
api.add_resource(CurrentUserMembersResource, '/api/current_user_details/members')
api.add_resource(CurrentUserPurchasesResource, '/api/current_user_details/purchases')
api.add_resource(CreditConversionResource, '/api/credit_conversion')
