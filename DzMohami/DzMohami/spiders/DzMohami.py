import scrapy 
import re
from DzMohami.items import DzmohamiItem
import uuid

class DzMohamiSpider(scrapy.Spider):
    name = 'dzmohami'
    
    def start_requests(self):
        url = "https://avocatalgerien.com/"
        yield scrapy.Request(url, meta=dict(
                playwright=True,
                playwright_include_page=True,
            ),
            errback=self.errback_close_page,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        mohami_links = []
        try:
            mohami_links = await page.query_selector_all(".entry-title a")
        except: 
            pass

        if(len(mohami_links)>0):
            for mohami_link in mohami_links:
                mohami_link_text = await mohami_link.evaluate("(element)=>element.href")
                yield scrapy.Request(mohami_link_text, meta=dict(
                        playwright=True,
                        playwright_include_page=True,
                    ),
                    callback=self.mohami_parse,
                    errback=self.errback_close_page
                )

        
        await page.wait_for_timeout(2000)
        next_button = None
        try: 
            next_button = await page.wait_for_selector("a.next") 
        except: 
            pass

        if(next_button is not None): 
            next_link = await next_button.evaluate("(element)=> element.href")
            yield scrapy.Request(next_link, meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                ),
                callback=self.parse, 
                errback=self.errback_close_page
            )
        
        await page.close() 
        
    
    async def mohami_parse(self, response): 
        page = response.meta["playwright_page"]


        # function to extract fname and name
        def extract_names(full_name):
            cleaned_name = full_name.lower().replace("maitre", "").strip()
    
            # Split the cleaned name into words
            name_parts = re.split(r'\s+', cleaned_name)
    
            # The first word is the first name, and the rest are the last name
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
            
            return first_name, last_name
        # --- full name ---
        full_name = ""
        fname = "" 
        name = ""
        try: 
            full_name_url = await page.wait_for_selector(".vcard a")
            full_name = await full_name_url.evaluate("(element)=>element.textContent")
        except: 
            pass
        if(len(full_name)>0): 
            result = extract_names(full_name)
            if(len(result[0]) and len(result[1])): 
                fname = result[0]
                name = result[1]
            elif(len(result[0]) ): 
                fname = result[0]
                name = result[0]
            else: 
                fname = "hasNofName"
                name = "hasNoName"

        
        # --- email ---
        email_text = ""
        try: 
            email = await page.query_selector("#listing-email a")
            email_text = await email.evaluate("(element)=>element.textContent")
        except: 
            pass

        
        
        # --- phone number ---
        phone_numbers = []
        phone_element_text = ""
        try: 
            phone = await page.wait_for_selector(".reveal span")
            await phone.click()
            await page.wait_for_timeout(10000)
        except: 
            pass
        try : 
            phone_element = await page.wait_for_selector(".reveal")
            phone_element_text = await phone_element.evaluate("(element)=>element.textContent")
            phone_numbers_text = re.sub(r'[^0-9/]', '', phone_element_text)
            phone_numbers_array = phone_numbers_text.split()
            for phone_number in phone_numbers_array: 
                try: 
                    if(int(phone_number)): 
                        phone_numbers.append(phone_number)
                except: pass
        except: 
            pass
        

        # --- address text ---
        adress_text = ""
        try:
            adress = await page.wait_for_selector(".address")
            adress_text = await adress.evaluate("(element)=> element.textContent")
        except: 
            pass

        # wilaya 
        wilaya = ""
        try: 
            if(len(adress_text)):
                wilayas = ["adrar","chlef","laghouat","oum el bouaghi","batna","bejaia","biskra","bechar","blida","bouira","tamanrasset","tebessa","tlemcen","tiaret","tizi ouzou","alger","djelfa","jijel","setif","saida","skikda","sidi bel abbes","annaba","guelma","constantine","medea","mostaganem","msila","mascara","ouargla","oran","el bayadh","illizi","borj bou arreridj","boumerdes","el taref","tindouf","tissemsilt","el oued","khenchela","souk ahras","tipaza","mila","ain defla","naama","ain temouchent","ghardaia","relizane","algérie"]
                wilayas_pattern = re.compile(r'\b(?:' + '|'.join(wilayas) + r')\b', re.IGNORECASE)
                wilaya = wilayas_pattern.findall(adress_text.lower())
                if(len(wilaya)>0): 
                    wilaya = wilaya[0]
        except: pass

        # langitude et latitude 
        latitude = "0"
        longitude = "0"
        try: 
            metas_long_lati = await page.query_selector_all(".details-left>div>div meta")
            if(len(metas_long_lati)>0):
                latitude = await metas_long_lati[0].evaluate("(element)=>element.attributes['content'].value")                
                longitude = await metas_long_lati[1].evaluate("(element)=>element.attributes['content'].value")
        except: 
            pass
        print("\n\n\n logitude \n\n\n")
        print(longitude)

        # description 
        description = ""
        try: 
            all_descriptions =  await page.query_selector_all("#overview p")
            if(len(all_descriptions)>0):
                for p_element in all_descriptions:
                    try:
                        p_content = await p_element.evaluate("(element)=>element.textContent")
                        description = description + p_content
                    except:
                        pass
        except:
            pass



        # --- image ---
        avocat_image_link = ""
        try: 
            avocat_image = await page.query_selector(".listing_thumbnail")
            avocat_image_link = await avocat_image.evaluate("(element)=>element.src")
        except: 
            pass


        # --- categories ---
        categories = []
        try:
            categorie_parent = await page.query_selector_all(".listing-cat a")
        except:
            pass
        for cat in categorie_parent: 
            cat_text = await cat.evaluate("(element)=>element.textContent")
            categories.append(cat_text)
        


        # schedule 
        schedule = []


        # rating
        rating = "0"
        rating_element = await page.wait_for_selector(".stars")
        if(rating_element is not None): 
            rating = await rating_element.evaluate("(element)=>element.classList[1].split('-')[1]")
        
        

        # comments with their rating
        comments = []
        if(float(rating)>0):
            try:
                reviews_tab = await page.wait_for_selector("#reviews-tab")
                await reviews_tab.click()
                await page.wait_for_timeout(2000)
                comments_holder = []
                try:
                    comments_holder = await page.query_selector_all("#review-4")
                except : pass
                if(len(comments_holder)>0):
                    for comment in comments_holder: 
                        comment_obj = {}
                        user_name = ""
                        try:
                            user_name_element = await comment.query_selector(".review-author-meta a")
                            user_name = await user_name_element.evaluate("(element)=>element.textContent")
                        except: pass
                        stars_value = "0"
                        try:
                            stars_element = await comment.query_selector(".review-content .stars")
                            stars_value = await stars_element.evaluate("(element)=>element.classList[1].split('-')[1]")
                        except: pass
                        date_value =""
                        try: 
                            date_element = await comment.query_selector(".review-content .review-date a")
                            date_value = await date_element.evaluate("(element)=>element.textContent")
                        except: pass
                        reveiw_content = ""
                        try: 
                            reveiw_content_element = await comment.query_selector(".review-content .review-body")
                            reveiw_content = await reveiw_content_element.evaluate("(element)=>element.textContent")
                        except: pass

                        comment_obj["user"] = user_name
                        comment_obj["stars_value"] = float(stars_value)
                        comment_obj["date"] = date_value
                        comment_obj["review_content"] = reveiw_content
                        comments.append(comment_obj)
            except :pass

        # social media 
        social = ""
        try:
            social_element = await page.query_selector("#listing-follow a")
            social = await social_element.evaluate("(element)=>element.href")
        except: 
            pass
        
        try: 
            rating = float(rating)
            longitude = float(longitude)
            latitude = float(latitude)
        except: 
            pass
        if(len(phone_numbers)>0): 
            phone_numbers = phone_numbers[0]
        else: 
            phone_numbers = "0000000000"
        
        if(len(email_text)==0): 
            unique_email = f"hasNoEmail_{str(uuid.uuid4())}@gmail.com"
            email_text = unique_email
        

        mohami_item = DzmohamiItem()

        mohami_item['name'] = name 
        mohami_item['fname'] = fname
        mohami_item['email'] = email_text 
        mohami_item['phone'] = phone_numbers
        mohami_item['address'] = adress_text 
        mohami_item['description'] = description
        mohami_item['avocat_image'] = avocat_image_link
        mohami_item['categories'] = categories
        mohami_item['schedule'] = schedule
        mohami_item['rating'] = rating
        mohami_item['comments'] = comments
        mohami_item['social'] = social
        mohami_item['wilaya'] = wilaya
        mohami_item['longitude'] = longitude
        mohami_item['latitude'] = latitude
        
        yield mohami_item
        await page.close()

    async def errback_close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        print("---------------errror--------------", failure)
        await page.close()
