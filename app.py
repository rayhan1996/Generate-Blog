import streamlit as st
import openai
import time
from openai import OpenAI
import requests
import os

print(st.secrets)
# Access the API key securely
api_key = st.secrets["OPENAI_API_KEY"]

# Set the OpenAI API key
openai.api_key = api_key

# Test the API
response = openai.Model.list()
st.write("Available models:", response)

# Create an OpenAI client instance
client = OpenAI(api_key=api_key)

# Use the client for operations
print("OpenAI client initialized successfully!")


# Function to send the prompt to the OpenAI API and get the response
def get_generated_text(prompt_text, max_tokens):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a skilled Farsi content creator. Your task is to write clear,non-repetitive, coherent, and engaging articles with a formal tone and appropriate use of literary devices. Ensure the content is SEO-friendly and follows proper punctuation rules."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=max_tokens,
            temperature=0.8
        )

        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return ""

# Function to generate H2 titles based on user input
def generate_h2_titles(parameters):
    prompt = f"""
    مقدمه در ابتدا آورده شده در ادامه با توجه به موضوع مقاله "{parameters['topic']}" و به تعدادی که کاربر مشخص کرده {parameters['h2_count']}، صرفا زیر عنوان های مورد نیاز مقاله را بدون توضیح ، بنویسید.

    اطلاعات مخاطب:
    - لحن مقاله: {parameters['tone']}
    - سبک محتوا: {parameters['style']}
    - هدف مقاله: {parameters['purpose']}
    - کلمات کلیدی مورد استفاده: {parameters['include_keywords']}
    - کلمات کلیدی که نباید استفاده شوند: {parameters['avoid_keywords']}
    - میزان استفاده از ارایه های ادبی: {parameters['figures_of_speech']}
    """
    titles_response = get_generated_text(prompt, max_tokens=500)
    h2_titles = titles_response.split('\n')
    return [title.strip() for title in h2_titles if title.strip()]

# Function to generate the introduction with meta title
def generate_introduction(topic, parameters):
    prompt = f"""
    لطفاً مقدمه‌ای جامع و خلاقانه و با پرهیز از تکرار محتوا برای مقاله با عنوان "{topic}" بنویسید.

    اطلاعات مخاطب:
    - لحن مقاله: {parameters['tone']}
    - سبک محتوا: {parameters['style']}
    - هدف مقاله: {parameters['purpose']}
    - کلمات کلیدی مورد استفاده: {parameters['include_keywords']}
    - کلمات کلیدی که نباید استفاده شوند: {parameters['avoid_keywords']}
    - آیا نیاز به عنوان متا داریم؟: {parameters['meta_title']}
    - میزان استفاده از ارایه های ادبی: {parameters['figures_of_speech']}
    - در صورت نیاز به meta_title پس از مقدمه آورده شود
    - لطفاً مقدمه‌ای قوی بنویسید که خواننده را جذب کند و موضوع مقاله را به‌وضوح معرفی کند.
    - به کارگیری آرایه های ادبی زبان فارسی متناسب با محتوا و ساختار جمله
    - تمامی اصول سئو (SEO) و بهینه‌سازی برای موتورهای جستجو
    - استفاده از علائم نگارشی استاندارد زبان فارسی
    """
    return get_generated_text(prompt, max_tokens=15000)

# Function to generate content for each H2 section
def generate_h2_section(h2_title, previous_text, parameters):
    prompt = f"""
    لطفا بخشی از مقاله را با توجه به "{h2_title}"  و متن قبلی تولید شده، بنویسید.

    متن قبلی
    {previous_text}

    اطلاعات مخاطب:
    - لحن مقاله: {parameters['tone']}
    - سبک محتوا: {parameters['style']}
    - هدف مقاله: {parameters['purpose']}
    - کلمات کلیدی مورد استفاده: {parameters['include_keywords']}
    - کلمات کلیدی که نباید استفاده شوند: {parameters['avoid_keywords']}
    - میزان استفاده از ارایه های ادبی: {parameters['figures_of_speech']}
    - به کارگیری آرایه های ادبی زبان فارسی متناسب با محتوا و ساختار جمله
    - رعایت تمامی اصول سئو (SEO) و بهینه‌سازی برای موتورهای جستجو
    - استفاده از علائم نگارشی استاندارد زبان فارسی
    - پرهیز از تکرار محتوا و توجه به خلاقانه بودن محتوا
    لطفاً مطالب را با انسجام و پیوستگی کامل ارائه دهید.
    """
    return get_generated_text(prompt, max_tokens=16000)

# Function to generate the conclusion
def generate_conclusion(previous_text, parameters):
    prompt = f"""
    لطفاً نتیجه‌گیری مقاله بر اساس متن قبلی  بنویسید.

    متن قبلی:
    {previous_text}

    اطلاعات مخاطب:
    - لحن مقاله: {parameters['tone']}
    - سبک محتوا: {parameters['style']}
    - هدف مقاله: {parameters['purpose']}
    - کلمات کلیدی مورد استفاده: {parameters['include_keywords']}
    - کلمات کلیدی که نباید استفاده شوند: {parameters['avoid_keywords']}
    - میزان استفاده از ارایه های ادبی: {parameters['figures_of_speech']}

    نتیجه‌گیری باید خلاصه‌ای از نکات کلیدی باشد و از تکرار محتوا جلوگیری شود و به خواننده احساس رضایت از مطالعه مقاله بدهد.
    - به کارگیری آرایه های ادبی زبان فارسی متناسب با محتوا و ساختار جمله
    - تمامی اصول سئو (SEO) و بهینه‌سازی برای موتورهای جستجو
    - استفاده از علائم نگارشی استاندارد زبان فارسی
    """
    return get_generated_text(prompt, max_tokens=15000)

# Function to generate the full blog post
def generate_full_blog(topic, parameters):
    # Generate H2 titles
    h2_titles = generate_h2_titles(parameters)

    # Generate the introduction
    introduction = generate_introduction(topic, parameters)

    # Generate content for each H2 section
    h2_sections = ""
    previous_text = introduction
    for h2_title in h2_titles:
        section_text = generate_h2_section(h2_title, previous_text, parameters)
        h2_sections += f"\n{section_text}\n\n"
        previous_text += section_text  # Update previous_text with each section to maintain context

    # Generate the conclusion
    conclusion = generate_conclusion(previous_text, parameters)

    # Combine all parts to form the full article
    full_blog_text = f"عنوان مقاله: {topic}\n\n{introduction}\n\n{h2_sections}\n\n{conclusion}"
    return full_blog_text.strip()

# Streamlit UI
st.title("Farsi Content Generator")
topic = st.text_input("Enter the Topic:", "سرعت رشد تکنولوژی")
parameters = {
    "tone": st.selectbox("Select Tone:", ["عامیانه", "رسمی"]),
    "style": st.selectbox("Select Style:", ["طنز", "جدی"]),
    "topic": topic,
    "purpose": st.selectbox("Select Purpose:", ["بلاگ", "لندینگ پیج", "محصول"]),
    "avoid_keywords": st.text_input("Avoid Keywords:", "ماشین"),
    "include_keywords": st.text_input("Include Keywords:", "گوشی، موبایل، لپ‌تاپ، هوش مصنوعی"),
    "h2_count": st.slider("Number of H2 Titles:", 1, 10, 6),
    "meta_title": st.selectbox("Include Meta Title:", ["داشته باشد", "نداشته باشد"]),
    "figures_of_speech": st.selectbox("Figures of Speech:", ["کم", "متوسط", "زیاد"])
}

if st.button("Generate Blog"):
    with st.spinner("Generating blog..."):
        start_time = time.time()
        blog_text = generate_full_blog(topic, parameters)
        end_time = time.time()
        st.success("Blog generated successfully!")
        st.write(blog_text)
        st.write(f"Time taken: {end_time - start_time:.2f} seconds")
