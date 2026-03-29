
const targets = [
  { id: 76, name: "Odeko", yc: "https://www.ycombinator.com/companies/odeko" },
  { id: 77, name: "GitPrime", yc: "https://www.ycombinator.com/companies/gitprime" },
  { id: 78, name: "Proxy", yc: "https://www.ycombinator.com/companies/proxy" },
  { id: 79, name: "FutureAdvisor", yc: "https://www.ycombinator.com/companies/futureadvisor" },
  { id: 80, name: "Podium", yc: "https://www.ycombinator.com/companies/podium" },
  { id: 81, name: "Rappi", yc: "https://www.ycombinator.com/companies/rappi" },
  { id: 82, name: "Razorpay", yc: "https://www.ycombinator.com/companies/razorpay" },
  { id: 83, name: "Rippling", yc: "https://www.ycombinator.com/companies/rippling" },
  { id: 84, name: "Scale AI", yc: "https://www.ycombinator.com/companies/scale-ai" },
  { id: 85, name: "Scentbird", yc: "https://www.ycombinator.com/companies/scentbird" },
  { id: 86, name: "Scribd", yc: "https://www.ycombinator.com/companies/scribd" },
  { id: 87, name: "ShipBob", yc: "https://www.ycombinator.com/companies/shipbob" },
  { id: 88, name: "SmartAsset", yc: "https://www.ycombinator.com/companies/smartasset" },
  { id: 89, name: "Stripe", yc: "https://www.ycombinator.com/companies/stripe" },
  { id: 90, name: "Wave", yc: "https://www.ycombinator.com/companies/wave" },
  { id: 91, name: "Webflow", yc: "https://www.ycombinator.com/companies/webflow" },
  { id: 92, name: "Whatnot", yc: "https://www.ycombinator.com/companies/whatnot" },
  { id: 93, name: "Zapier", yc: "https://www.ycombinator.com/companies/zapier" },
  { id: 94, name: "Zepto", yc: "https://www.ycombinator.com/companies/zepto" },
  { id: 95, name: "Focal Systems", yc: "https://www.ycombinator.com/companies/focal-systems" },
  { id: 96, name: "Mio", yc: "https://www.ycombinator.com/companies/mio" },
  { id: 97, name: "Daily", yc: "https://www.ycombinator.com/companies/daily" },
  { id: 98, name: "Petcube", yc: "https://www.ycombinator.com/companies/petcube" },
  { id: 99, name: "Outschool", yc: "https://www.ycombinator.com/companies/outschool" },
  { id: 100, name: "Mason", yc: "https://www.ycombinator.com/companies/mason" }
];

const fallbackEmail = "robertdemottojr83@gmail.com";

async function scrape() {
  const results = [];
  for (const target of targets) {
    console.error(`Scraping ${target.name}...`);
    let website = null;
    let email = fallbackEmail;

    try {
      const ycResponse = await fetch(target.yc, { headers: { 'User-Agent': 'Mozilla/5.0' } });
      const ycHtml = await ycResponse.text();
      
      // Extract website
      const websiteMatch = ycHtml.match(/data-tooltip-content="(https?:\/\/[^"]+)" aria-label="Company website"/);
      if (websiteMatch) {
        website = websiteMatch[1];
      } else {
        // Fallback website extraction
        const altMatch = ycHtml.match(/href="(https?:\/\/[^"]+)"[^>]*aria-label="Company website"/);
        if (altMatch) website = altMatch[1];
      }

      if (website) {
        try {
          const siteResponse = await fetch(website, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(5000) });
          const siteHtml = await siteResponse.text();
          const emailMatch = siteHtml.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g);
          if (emailMatch) {
            for (const foundEmail of emailMatch) {
              if (
                !/\.(png|jpg|jpeg|gif|svg|webp|woff|woff2|ttf|otf|avif)$/i.test(foundEmail) &&
                !foundEmail.includes('sentry.io') &&
                !foundEmail.includes('gitprime.com') && // sometimes domain matches
                foundEmail !== 'name@company.com' &&
                foundEmail !== 'example@example.com' &&
                foundEmail !== 'email@address.com' &&
                foundEmail !== 'your@email.com' &&
                !foundEmail.startsWith('u00') // sometimes unicode escaping issues
              ) {
                email = foundEmail;
                break;
              }
            }
          }
        } catch (e) {
          console.error(`Failed to fetch website ${website}: ${e.message}`);
        }
      }
    } catch (e) {
      console.error(`Failed to fetch YC page ${target.yc}: ${e.message}`);
    }

    results.push({
      id: target.id,
      name: target.name,
      yc_link: target.yc,
      website: website || "not found",
      email: email
    });
  }
  console.log(JSON.stringify(results, null, 2));
}

scrape();
