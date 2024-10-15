import json
import logging
import requests
from allure import attach, step
from allure_commons.types import AttachmentType
from selene import browser, be, have

base_url = 'https://demowebshop.tricentis.com'
LOGIN = 'gurualex@test.com'
PASSWORD = '123321'


def auth_cookie():
    response = requests.post(
        url=base_url + '/login',
        data={'Email': LOGIN, 'Password': PASSWORD, 'RememberMe': False},
        allow_redirects=False
    )
    auth = dict()
    auth['NOPCOMMERCE.AUTH'] = response.cookies.get('NOPCOMMERCE.AUTH')
    return auth


def add_product_to_cart():
    response = requests.post(
        url=base_url + '/addproducttocart/catalog/31/1/1',
        cookies=auth_cookie()
    )
    attach(body=response.request.url, name='Request', attachment_type=AttachmentType.TEXT,
           extension="txt")
    attach(body=json.dumps(dict(response.request.headers),
                           indent=4, ensure_ascii=True), name='Request Headers',
           attachment_type=AttachmentType.JSON,
           extension="json")
    attach(body=json.dumps(response.json(),
                           indent=4, ensure_ascii=True), name="Response", attachment_type=AttachmentType.JSON,
           extension="json")
    attach(body=str(response.cookies.get('Nop.customer')), name="Cookies", attachment_type=AttachmentType.TEXT,
           extension="txt")
    logging.info(response.request.url)
    logging.info(response.status_code)
    logging.info(response.text)


def remove_product_from_cart():
    browser.element('[name="removefromcart"]').click()
    browser.element('[name="updatecart"]').click()


def test_login():
    with step('Set cookie from API'):
        browser.open(base_url)
        browser.driver.add_cookie({'name': 'NOPCOMMERCE.AUTH', 'value': auth_cookie().get('NOPCOMMERCE.AUTH')})

    with step('Open main page'):
        browser.open(base_url)

    with step('Verify successful authorization'):
        browser.element(".account").should(have.text(LOGIN))

    with step('Close browser'):
        browser.quit()


def test_add_product_to_cart():
    with step('Add product to cart by API'):
        add_product_to_cart()

    with step('Set cookies from API'):
        browser.open(base_url + '/cart')
        browser.driver.add_cookie({'name': 'NOPCOMMERCE.AUTH', 'value': auth_cookie().get('NOPCOMMERCE.AUTH')})

    with step('Open cart page'):
        browser.open(base_url + '/cart')

    with step('Verify availability of product in cart and its quantity'):
        browser.element('.cart').element('.product').element('['
                                                             'href="/141-inch-laptop"]').should(be.visible)
        browser.element('.qty-input').should(have.attribute('value', '1'))

    with step('Clear cart'):
        remove_product_from_cart()

    with step('Close browser'):
        browser.quit()


def test_remove_product_from_cart():
    with step('Add product to cart'):
        add_product_to_cart()

    with step('Set cookies from API'):
        browser.open(base_url + '/cart')
        browser.driver.add_cookie({'name': 'NOPCOMMERCE.AUTH', 'value': auth_cookie().get('NOPCOMMERCE.AUTH')})

    with step('Open cart page'):
        browser.open(base_url + '/cart')

    with step('Remove product from cart'):
        remove_product_from_cart()

    with step('Verify removing of product from cart'):
        browser.element('.order-summary-content').should(have.exact_text('Your Shopping Cart is empty!'))

    with step('Close browser'):
        browser.quit()


def test_logout():
    with step('Set cookie from API'):
        browser.open(base_url)
        browser.driver.add_cookie({'name': 'NOPCOMMERCE.AUTH', 'value': auth_cookie().get('NOPCOMMERCE.AUTH')})

    with step('Open main page'):
        browser.open(base_url)

    with step('Logout'):
        browser.element('[href="/logout"]').click()

    with step('Verify successful logout'):
        browser.element('[href="/login"]').should(be.visible)

    with step('Close browser'):
        browser.quit()