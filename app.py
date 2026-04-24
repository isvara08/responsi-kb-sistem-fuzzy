from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


def trapezoid(x, a, b, c, d):
    """Fungsi keanggotaan trapesium"""
    if x < a or x > d:
        return 0.0
    elif a <= x < b:
        return (x - a) / (b - a) if b != a else 1.0
    elif b <= x <= c:
        return 1.0
    elif c < x <= d:
        return (d - x) / (d - c) if d != c else 1.0
    return 0.0


def triangle(x, a, b, c):
    """Fungsi keanggotaan segitiga"""
    if x < a or x > c:
        return 0.0
    elif a <= x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    elif b < x <= c:
        return (c - x) / (c - b) if c != b else 1.0
    return 0.0


def fuzzify_heart_rate(hr):
    """Fuzzifikasi detak jantung"""
    return {
        'normal': trapezoid(hr, 50, 60, 90, 100),
        'cepat': triangle(hr, 90, 115, 140),
        'sangat_cepat': trapezoid(hr, 130, 140, 190, 200)
    }


def fuzzify_temperature(temp):
    """Fuzzifikasi suhu tubuh"""
    return {
        'normal': trapezoid(temp, 35, 35.5, 37, 37.5),
        'hangat': triangle(temp, 37, 37.8, 38.5),
        'panas': trapezoid(temp, 38, 38.5, 41, 42)
    }


def fuzzify_duration(dur):
    """Fuzzifikasi lama latihan"""
    return {
        'singkat': trapezoid(dur, 0, 5, 35, 45),
        'sedang': triangle(dur, 30, 60, 90),
        'lama': trapezoid(dur, 75, 90, 160, 180)
    }


def evaluate_rules(hr_fuzzy, temp_fuzzy, dur_fuzzy):
    """Evaluasi aturan fuzzy Sugeno"""
    rules = []
    
    # Output values: Aman=0, Waspada=50, Berbahaya=100
    OUTPUT_AMAN = 0
    OUTPUT_WASPADA = 50
    OUTPUT_BERBAHAYA = 100
    
    # Rule 1: Normal, Normal, Singkat -> Aman
    alpha = min(hr_fuzzy['normal'], temp_fuzzy['normal'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_AMAN))
    
    # Rule 2: Normal, Normal, Sedang -> Aman
    alpha = min(hr_fuzzy['normal'], temp_fuzzy['normal'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_AMAN))
    
    # Rule 3: Normal, Hangat, Singkat -> Waspada
    alpha = min(hr_fuzzy['normal'], temp_fuzzy['hangat'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 4: Normal, Hangat, Sedang -> Waspada
    alpha = min(hr_fuzzy['normal'], temp_fuzzy['hangat'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 5: Normal, Panas, Singkat -> Waspada
    alpha = min(hr_fuzzy['normal'], temp_fuzzy['panas'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 6: Cepat, Normal, Singkat -> Aman
    alpha = min(hr_fuzzy['cepat'], temp_fuzzy['normal'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_AMAN))
    
    # Rule 7: Cepat, Normal, Sedang -> Waspada
    alpha = min(hr_fuzzy['cepat'], temp_fuzzy['normal'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 8: Cepat, Hangat, Singkat -> Waspada
    alpha = min(hr_fuzzy['cepat'], temp_fuzzy['hangat'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 9: Cepat, Hangat, Sedang -> Berbahaya
    alpha = min(hr_fuzzy['cepat'], temp_fuzzy['hangat'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 10: Cepat, Panas, Singkat -> Berbahaya
    alpha = min(hr_fuzzy['cepat'], temp_fuzzy['panas'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 11: Sangat Cepat, Normal, Singkat -> Waspada
    alpha = min(hr_fuzzy['sangat_cepat'], temp_fuzzy['normal'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_WASPADA))
    
    # Rule 12: Sangat Cepat, Normal, Sedang -> Berbahaya
    alpha = min(hr_fuzzy['sangat_cepat'], temp_fuzzy['normal'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 13: Sangat Cepat, Hangat, Singkat -> Berbahaya
    alpha = min(hr_fuzzy['sangat_cepat'], temp_fuzzy['hangat'], dur_fuzzy['singkat'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 14: Sangat Cepat, Hangat, Sedang -> Berbahaya
    alpha = min(hr_fuzzy['sangat_cepat'], temp_fuzzy['hangat'], dur_fuzzy['sedang'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 15: Sangat Cepat, Panas, Apapun -> Berbahaya
    alpha = min(hr_fuzzy['sangat_cepat'], temp_fuzzy['panas'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 16: Apapun, Panas, Lama -> Berbahaya
    alpha = min(temp_fuzzy['panas'], dur_fuzzy['lama'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    # Rule 17: Sangat Cepat, Apapun, Lama -> Berbahaya
    alpha = min(hr_fuzzy['sangat_cepat'], dur_fuzzy['lama'])
    if alpha > 0:
        rules.append((alpha, OUTPUT_BERBAHAYA))
    
    return rules


def defuzzify(rules):
    """Defuzzifikasi dengan rata-rata terbobot"""
    if not rules:
        return 0
    
    numerator = sum(alpha * z for alpha, z in rules)
    denominator = sum(alpha for alpha, _ in rules)
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def get_risk_level(value):
    """Menentukan level risiko berdasarkan nilai crisp"""
    if 0 <= value <= 40:
        return 'Aman', 'green'
    elif 41 <= value <= 70:
        return 'Waspada', 'yellow'
    else:
        return 'Berbahaya', 'red'


def calculate_heatstroke_risk(heart_rate, temperature, duration):
    """Fungsi utama untuk menghitung risiko heatstroke"""
    # Fuzzifikasi
    hr_fuzzy = fuzzify_heart_rate(heart_rate)
    temp_fuzzy = fuzzify_temperature(temperature)
    dur_fuzzy = fuzzify_duration(duration)
    
    # Evaluasi aturan
    rules = evaluate_rules(hr_fuzzy, temp_fuzzy, dur_fuzzy)
    
    # Defuzzifikasi
    crisp_output = defuzzify(rules)
    
    # Tentukan level risiko
    risk_level, color = get_risk_level(crisp_output)
    
    return {
        'crisp_output': round(crisp_output, 2),
        'risk_level': risk_level,
        'color': color,
        'fuzzy_values': {
            'heart_rate': hr_fuzzy,
            'temperature': temp_fuzzy,
            'duration': dur_fuzzy
        },
        'active_rules': len(rules)
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pertanyaan')
def pertanyaan():
    return render_template('pertanyaan.html')


@app.route('/hasil', methods=['GET', 'POST'])
def hasil():
    if request.method == 'POST':
        heart_rate = float(request.form.get('heart_rate', 70))
        temperature = float(request.form.get('temperature', 36.5))
        duration = float(request.form.get('duration', 30))
    else:
        heart_rate = float(request.args.get('heart_rate', 70))
        temperature = float(request.args.get('temperature', 36.5))
        duration = float(request.args.get('duration', 30))
    
    result = calculate_heatstroke_risk(heart_rate, temperature, duration)
    return render_template('hasil.html', result=result, 
                          heart_rate=heart_rate, 
                          temperature=temperature, 
                          duration=duration)


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    heart_rate = float(data.get('heart_rate', 70))
    temperature = float(data.get('temperature', 36.5))
    duration = float(data.get('duration', 30))
    
    result = calculate_heatstroke_risk(heart_rate, temperature, duration)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
