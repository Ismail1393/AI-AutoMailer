const axios = require("axios");
const fs = require("fs");
const cheerio = require("cheerio");

async function getPersonDetails(personId) {
  const url = `https://www.careershift.com/App/Contacts/SearchDetails?personId=${personId}`;

  const headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    Accept:
      "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    Cookie:
      "ASP.NET_SessionId=ywoxsdtmoqiokbtgcszsc0vt; _ga=GA1.1.1601969420.1729201257; __RequestVerificationToken=5JQXUbCtSIzYVgOUI9bMS6NMEOqPZgC68c1KKSQ_SafhKN3IfuTvH7fysBDOCOX7JZ9yxnGB1FMJeFkKXSScCQ0fT1s1; .CS=AD3EF058C2BA7DA7E39B12FD6B1EFE9C7C018F73A272DD3D37CAABE453DA79E46F6266661CC1F647081375F718799CEFFA298D0E8D297C586F0DB5CA114982B28EB6E977397215825472F5FF3CC08E0CD148A275; .AspNet.ApplicationCookie=-8Wegk9afYwm_WbfXagKBe8wiOni9EoaSnXo16nnmWLQTiGPJ_3dwXAcKq0kkj3A3d6zdtFXt3tB6zr5Fc3KzLGUTAot9ocrg44l6zSkNyMoBl7cLFr6s491ViU8hNYdmQ_03Mqz8UBQS4ICPqGl93A8eCCefpZxFOd-SApmI4jjkpxBnJLYoC-J_uVlG9WQGP52-rLBF29kX-C8_66tMGowv9hMKD5lkFnPLAkvE3rfVer0DLGxuuiEjiEEIVRFiL0dU9ZaxFasfkp72cWUEHLx3Ld-gTBT-s3CWJ94xTl47zl3WUpNugMta2YRbgZpASSq8Wi1rYzQj6QGJHuEEtk96viRZkDHB0Zpi4cXmqlJgm6uogNPInxCeOVnf3-buPI03Q; user_nav_menu_collapsed=true; main_nav_menu_collapsed=true; _ga_WCXNQG3WYC=GS1.1.1729201256.1.1.1729201325.0.0.0",
    Referer: "https://www.careershift.com/App/Contacts/Search",
  };

  try {
    const response = await axios.get(url, { headers });
    const $ = cheerio.load(response.data);

    const a = $.html();

    // Extract relevant information
    const name = $(".meta .title").first().text().trim();
    const position = $(".meta h3").text().trim();
    const company = $(".meta .title.pt-2.d-inline-flex").text().trim();
    const fax = $(".phone-block #fax").text().trim();
    const location = $(".location").first().text().trim();
    const industries = $(".location")
      .next()
      .text()
      .replace("Industries include: ", "")
      .trim();
    const email = $('a[href^="mailto:"]').attr("href")
      ? $('a[href^="mailto:"]').attr("href").replace("mailto:", "")
      : "N/A";
    const phone = $("span#fax").text().trim() || "N/A";
    // Create JSON object for contact details
    const contactDetails = {
      personId,
      name,
      position,
      company,
      fax,
      location,
      industries,
      email,
      phone,
      linkedin: $('a[aria-label^="Search LinkedIn"]').attr("href"),
    };

    return contactDetails;
  } catch (error) {
    console.error(`Error getting details for personId ${personId}:`, error);
    return null;
  }
}

async function sendRequest() {
  const url = "https://www.careershift.com/App/Contacts/Search";

  const headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent":
      "copy from cookies on browser",
    Accept:
      "copy from cookies on browser",
    Cookie:
      "copy from cookies on browser",
    Referer: "https://www.careershift.com/App/Contacts/Search",
  };

  let currentPage = 0;
  let totalPages = 5; // Initial assumption, this can be dynamically updated based on the response
  let allPersonIds = [];
  let allContactDetails = [];

  while (currentPage < totalPages) {
    const formData = new URLSearchParams();
    formData.append(
      "__RequestVerificationToken",
      "Db9ZOOcgdSHlk7Vn4iX2aQZ_BBmeEpT148pOlfWChiVC35oC-3ZLIL0GhgpYM46aU3SvbkAte2VjXzA9NDQM86qyIlnuY-Dpj33mPy6SAckiYGyWcM2ZAeVgV705FPB1RJ8rgA2"
    );
    formData.append("FirstName", "");
    formData.append("LastName", "");
    formData.append("School", "");
    formData.append("CompanyName", "Google");
    formData.append("IndustryList", "Any");
    formData.append("LastUpdated", "");
    formData.append("Country", "USA");
    formData.append("State", "");
    formData.append("Region", "");
    formData.append("ZipCode", "");
    formData.append("ZipRadius", "");
    formData.append("LocationSearchType", "PersonOrHQ");
    formData.append("Title", "");
    formData.append("CurrentPage", currentPage.toString());
    formData.append("TotalPages", "0"); // TotalPages might be updated dynamically later
    formData.append("SearchId", "");
    formData.append("SavedSearchId", "");
    formData.append("IsPaging", "false");

    try {
      const response = await axios.post(url, formData.toString(), { headers });

      // Load the HTML response into cheerio
      const $ = cheerio.load(response.data);

      // Extract all personIds from the list items
      $("li.draggable-item").each((index, element) => {
        const personId = $(element).attr("data-id");
        if (personId) {
          allPersonIds.push(personId);
        }
      });

      console.log(`Page ${currentPage} person IDs:`, allPersonIds);

      // Assuming you can parse `TotalPages` from the response if available
      // totalPages = parseTotalPages(response.data);

      currentPage++;
    } catch (error) {
      console.error("Error making request for page", currentPage, ":", error);
      break;
    }
  }

  // Get details for all person IDs
  for (const personId of allPersonIds) {
    const details = await getPersonDetails(personId);
    if (details) {
      allContactDetails.push(details);
    }
  }

  // Save the contact details to a JSON file
  fs.writeFileSync(
    "google.json",
    JSON.stringify(allContactDetails, null, 2)
  );
  console.log("All contact details saved to google.json");
}

sendRequest();
