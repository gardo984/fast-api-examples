import {
  Controller,
  Get,
  Render,
} from '@nestjs/common';


@Controller()
export class AppController {
  @Get("/")
  @Render("index")
  index(){
    return {"name": "FooBar"}
  }

  @Get("/about")
  @Render("about")
  about(){
    let viewData = {};
    viewData["description"] = "This is an about page..";
    viewData["author"] = "Developed by: Manuel Lazo";
    viewData["title"] = "About us - Online Store";
    viewData["subtitle"] = "About us";
    return {
      viewData: viewData,
    }
  }
}