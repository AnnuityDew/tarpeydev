# import native Python packages

# import third party packages
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# import custom local stuff
from src.api.index import Quote, random_quote


# router and templates
index_views = APIRouter(prefix="")
templates = Jinja2Templates(directory='templates')


@index_views.get("/", response_class=HTMLResponse, tags=["simple_view"])
async def homepage(request: Request, quote: Quote = Depends(random_quote)):
    # generate color palette using Seaborn for the main site buttons
    return templates.TemplateResponse(
        'index/index.html',
        context={
            'request': request,
            'quote': quote,
        },
    )


@index_views.get("/colors", response_class=HTMLResponse, tags=["simple_view"])
def colors(request: Request):
    return templates.TemplateResponse(
        'index/colors.html',
        context={
            'request': request,
        },
    )


@index_views.get("/links", response_class=HTMLResponse, tags=["simple_view"])
def links(request: Request):
    return templates.TemplateResponse(
        'index/links.html',
        context={
            'request': request,
        },
    )


@index_views.get("/games", response_class=HTMLResponse, tags=["simple_view"])
def games(request: Request):
    return templates.TemplateResponse(
        'index/games.html',
        context={
            'request': request,
        },
    )
