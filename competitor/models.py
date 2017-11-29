from django.db import models
from django.contrib.auth.models import User


class Studio(models.Model):
    STATE_CHOICES = (
        (0, "AL"),
        (1, "AK"),
        (2, "AZ"),
        (3, "AR"),
        (4, "CA"),
        (5, "CO"),
        (6, "CT"),
        (7, "DE"),
        (8, "FL"),
        (9, "GA"),
        (10, "HI"),
        (11, "ID"),
        (12, "IL"),
        (13, "IN"),
        (14, "IA"),
        (15, "KS"),
        (16, "KY"),
        (17, "LA"),
        (18, "ME"),
        (19, "MD"),
        (20, "MA"),
        (21, "MI"),
        (22, "MN"),
        (23, "MS"),
        (24, "MO"),
        (25, "MT"),
        (26, "NE"),
        (27, "NV"),
        (28, "NH"),
        (29, "NJ"),
        (30, "NM"),
        (31, "NY"),
        (32, "NC"),
        (33, "ND"),
        (34, "OH"),
        (35, "OK"),
        (36, "OR"),
        (37, "PA"),
        (38, "RI"),
        (39, "SC"),
        (40, "SD"),
        (41, "TN"),
        (42, "TX"),
        (43, "UT"),
        (44, "VT"),
        (45, "VA"),
        (46, "WA"),
        (47, "WV"),
        (48, "WI"),
        (49, "WY")
    )
    COUNTRY_CHOICES = (
        (0, "Afghanistan"),
        (1, "Albania"),
        (2, "Algeria"),
        (3, "Andorra"),
        (4, "Angola"),
        (5, "Antigua and Barbuda"),
        (6, "Argentina"),
        (7, "Armenia"),
        (8, "Aruba"),
        (9, "Australia"),
        (10, "Austria"),
        (11, "Azerbaijan"),
        (12, "Bahamas, The"),
        (13, "Bahrain"),
        (14, "Bangladesh"),
        (15, "Barbados"),
        (16, "Belarus"),
        (17, "Belgium"),
        (18, "Belize"),
        (19, "Benin"),
        (20, "Bhutan"),
        (21, "Bolivia"),
        (22, "Bosnia and Herzegovina"),
        (23, "Botswana"),
        (24, "Brazil"),
        (25, "Brunei"),
        (26, "Bulgaria"),
        (27, "Burkina Faso"),
        (28, "Burma"),
        (29, "Burundi"),
        (30, "Cambodia"),
        (31, "Cameroon"),
        (32, "Canada"),
        (33, "Cabo Verde"),
        (34, "Central African Republic"),
        (35, "Chad"),
        (36, "Chile"),
        (37, "China"),
        (38, "Colombia"),
        (39, "Comoros"),
        (40, "Congo, Democratic Republic of the"),
        (41, "Congo, Republic of the"),
        (42, "Costa Rica"),
        (43, "Cote d'Ivoire"),
        (44, "Croatia"),
        (45, "Cuba"),
        (46, "Curacao"),
        (47, "Cyprus"),
        (48, "Czechia"),
        (49, "Denmark"),
        (50, "Djibouti"),
        (51, "Dominica"),
        (52, "Dominican Republic"),
        (53, "East Timor (see Timor-Leste)"),
        (54, "Ecuador"),
        (55, "Egypt"),
        (56, "El Salvador"),
        (57, "Equatorial Guinea"),
        (58, "Eritrea"),
        (59, "Estonia"),
        (60, "Ethiopia"),
        (61, "Fiji"),
        (62, "Finland"),
        (63, "France"),
        (64, "Gabon"),
        (65, "Gambia, The"),
        (66, "Georgia"),
        (67, "Germany"),
        (68, "Ghana"),
        (69, "Greece"),
        (70, "Grenada"),
        (71, "Guatemala"),
        (72, "Guinea"),
        (73, "Guinea-Bissau"),
        (74, "Guyana"),
        (75, "Haiti"),
        (76, "Holy See"),
        (77, "Honduras"),
        (78, "Hong Kong"),
        (79, "Hungary"),
        (80, "Iceland"),
        (81, "India"),
        (82, "Indonesia"),
        (83, "Iran"),
        (84, "Iraq"),
        (85, "Ireland"),
        (86, "Israel"),
        (87, "Italy"),
        (88, "Jamaica"),
        (89, "Japan"),
        (90, "Jordan"),
        (91, "Kazakhstan"),
        (92, "Kenya"),
        (93, "Kiribati"),
        (94, "Korea, North"),
        (95, "Korea, South"),
        (96, "Kosovo"),
        (97, "Kuwait"),
        (98, "Kyrgyzstan"),
        (99, "Laos"),
        (100, "Latvia"),
        (101, "Lebanon"),
        (102, "Lesotho"),
        (103, "Liberia"),
        (104, "Libya"),
        (105, "Liechtenstein"),
        (106, "Lithuania"),
        (107, "Luxembourg"),
        (108, "Macau"),
        (109, "Macedonia"),
        (110, "Madagascar"),
        (111, "Malawi"),
        (112, "Malaysia"),
        (113, "Maldives"),
        (114, "Mali"),
        (115, "Malta"),
        (116, "Marshall Islands"),
        (117, "Mauritania"),
        (118, "Mauritius"),
        (119, "Mexico"),
        (120, "Micronesia"),
        (121, "Moldova"),
        (122, "Monaco"),
        (123, "Mongolia"),
        (124, "Montenegro"),
        (125, "Morocco"),
        (126, "Mozambique"),
        (127, "Namibia"),
        (128, "Nauru"),
        (129, "Nepal"),
        (130, "Netherlands"),
        (131, "New Zealand"),
        (132, "Nicaragua"),
        (133, "Niger"),
        (134, "Nigeria"),
        (135, "North Korea"),
        (136, "Norway"),
        (137, "Oman"),
        (138, "Pakistan"),
        (139, "Palau"),
        (140, "Palestinian Territories"),
        (141, "Panama"),
        (142, "Papua New Guinea"),
        (143, "Paraguay"),
        (144, "Peru"),
        (145, "Philippines"),
        (146, "Poland"),
        (147, "Portugal"),
        (148, "Qatar"),
        (149, "Romania"),
        (150, "Russia"),
        (151, "Rwanda"),
        (152, "Saint Kitts and Nevis"),
        (153, "Saint Lucia"),
        (154, "Saint Vincent and the Grenadines"),
        (155, "Samoa"),
        (156, "San Marino"),
        (157, "Sao Tome and Principe"),
        (158, "Saudi Arabia"),
        (159, "Senegal"),
        (160, "Serbia"),
        (161, "Seychelles"),
        (162, "Sierra Leone"),
        (163, "Singapore"),
        (164, "Sint Maarten"),
        (165, "Slovakia"),
        (166, "Slovenia"),
        (167, "Solomon Islands"),
        (168, "Somalia"),
        (169, "South Africa"),
        (170, "South Korea"),
        (171, "South Sudan"),
        (172, "Spain"),
        (173, "Sri Lanka"),
        (174, "Sudan"),
        (175, "Suriname"),
        (176, "Swaziland"),
        (177, "Sweden"),
        (178, "Switzerland"),
        (179, "Syria"),
        (180, "Taiwan"),
        (181, "Tajikistan"),
        (182, "Tanzania"),
        (183, "Thailand"),
        (184, "Timor-Leste"),
        (185, "Togo"),
        (186, "Tonga"),
        (187, "Trinidad and Tobago"),
        (188, "Tunisia"),
        (189, "Turkey"),
        (190, "Turkmenistan"),
        (191, "Tuvalu"),
        (192, "Uganda"),
        (193, "Ukraine"),
        (194, "United Arab Emirates"),
        (195, "United Kingdom"),
        (196, "Uruguay"),
        (197, "Uzbekistan"),
        (198, "Vanuatu"),
        (199, "Venezuela"),
        (200, "Vietnam"),
        (201, "Yemen"),
        (202, "Zambia"),
        (203, "Zimbabwe")
    )
    name = models.CharField("Name", max_length=256)
    address = models.CharField("Address", max_length=512)
    city = models.CharField("City", max_length=256)
    state = models.IntegerField(
        "State", choices=STATE_CHOICES)
    zip_code = models.IntegerField("Zip Code")
    association_pin = models.IntegerField("Studio PIN")


class Dancer(models.Model):
    name = models.CharField("Name", max_length=256)
    email = models.CharField("Name", max_length=256)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE,
                               blank=True, null=True)
    profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )


class Request(models.Model):
    dancer = models.ForeignKey(Dancer, on_delete=models.CASCADE)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
